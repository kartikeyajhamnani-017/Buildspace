"""
Sentinel ML Engine v2.0 - Postgres Sink
Writes detection results to the `detections` table (see schema.sql).

This is the only file in the codebase that knows about Postgres.
SentinelMLEngine, worker.py's consume loop, and the test suites remain
fully database-agnostic — they only ever interact with the sink through
the same callable signature used by console_sink and jsonl_file_sink:

    sink(result, entry)

Plug it into worker.py by adding to the sink list:

    from postgres_sink import PostgresWriter, make_postgres_sink

    writer = PostgresWriter(dsn="postgresql://sentinel:sentinel@localhost:5432/sentinel_db")
    sinks  = [console_sink, make_postgres_sink(writer)]
"""

import logging

import psycopg2
import psycopg2.extras


logger = logging.getLogger('sentinel.postgres_sink')


class PostgresWriter:
    """
    Holds one persistent connection to Postgres and handles the
    write-and-recover lifecycle: insert a row, and if it fails, roll
    back the aborted transaction so the connection stays usable for
    the next insert rather than poisoning every subsequent write.

    One instance per worker process. Not thread-safe — if you later
    move to a multi-threaded sink dispatcher, give each thread its
    own PostgresWriter (or switch to a connection pool).
    """

    INSERT_SQL = """
        INSERT INTO detections (
            source_ip, ingestor_timestamp, request_type, payload,
            is_malicious, confidence, threat_level, detection_layer,
            attack_type, matched_rule, anomaly_score,
            detected_as, routing, routing_note,
            sequence_features, mitre_attack, processing_time_ms
        ) VALUES (
            %(source_ip)s, %(ingestor_timestamp)s, %(request_type)s, %(payload)s,
            %(is_malicious)s, %(confidence)s, %(threat_level)s, %(detection_layer)s,
            %(attack_type)s, %(matched_rule)s, %(anomaly_score)s,
            %(detected_as)s, %(routing)s, %(routing_note)s,
            %(sequence_features)s, %(mitre_attack)s, %(processing_time_ms)s
        )
    """

    def __init__(self, dsn):
        """
        Args:
            dsn (str): Postgres connection string, e.g.
                       "postgresql://sentinel:sentinel@localhost:5432/sentinel_db"
        """
        self.dsn  = dsn
        self.conn = None
        self._connect()

    def _connect(self):
        """Open a fresh connection. Autocommit so each insert is its
        own transaction — one bad row can't roll back rows already
        written successfully before it."""
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True
        logger.info("Connected to Postgres.")

    def write(self, row):
        """
        Insert one detection row.

        Args:
            row (dict): Must contain all keys referenced in INSERT_SQL.
                         Missing optional keys should be present as None,
                         not absent — psycopg2 needs every named placeholder
                         to exist in the mapping.

        Returns:
            bool: True on success, False if the write failed (logged,
                  connection recovered, caller's message is not lost from
                  Redis since this is called after analyze() already ran —
                  see the at-most-once note in worker.py for the broader
                  delivery guarantee this sits inside of).
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.INSERT_SQL, row)
            return True

        except psycopg2.OperationalError as e:
            # Connection itself died (Postgres restarted, network blip).
            # Attempt exactly one reconnect, then retry the write once.
            logger.error("Postgres connection lost: %s — reconnecting", e)
            try:
                self._connect()
                with self.conn.cursor() as cur:
                    cur.execute(self.INSERT_SQL, row)
                return True
            except Exception as retry_err:
                logger.error("Reconnect + retry failed: %s", retry_err)
                return False

        except Exception as e:
            # Bad data (e.g. malformed timestamp) aborts the transaction.
            # Roll back so the connection is usable for the NEXT insert —
            # without this, every subsequent write on this connection
            # would fail until the process restarts.
            logger.error("Insert failed, rolling back: %s — row=%r", e, row)
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Postgres connection closed.")


def _build_row(result, entry):
    """
    Map a SentinelMLEngine result dict + the original Go ingestor entry
    into the exact column set INSERT_SQL expects. Every key must be
    present (None where not applicable) since psycopg2 requires every
    named placeholder to resolve.
    """
    import json

    sequence_features = result.get('sequence_features')

    return {
        'source_ip':           entry.get('source_ip', 'unknown'),
        'ingestor_timestamp':  entry.get('timestamp'),
        'request_type':        (entry.get('request_type') or 'HTTP').upper().strip(),
        'payload':             entry.get('payload', ''),

        'is_malicious':        result['is_malicious'],
        'confidence':          result.get('confidence', 0.0),
        'threat_level':        result.get('threat_level', 'NONE'),
        'detection_layer':     result.get('detection_layer', ''),
        'attack_type':         result.get('attack_type'),
        'matched_rule':        result.get('matched_rule'),
        'anomaly_score':       result.get('anomaly_score'),

        'detected_as':         result.get('detected_as'),
        'routing':             result.get('routing'),
        'routing_note':        result.get('routing_note'),

        # JSONB column — psycopg2 needs an explicit Json() wrapper for dicts,
        # plain None is fine when Layer 3 didn't fire.
        'sequence_features':   psycopg2.extras.Json(sequence_features) if sequence_features else None,

        # Postgres TEXT[] — psycopg2 adapts Python lists automatically.
        # mitre_attack is sometimes an empty list, which is fine (not None).
        'mitre_attack':        result.get('mitre_attack') or [],

        'processing_time_ms':  result.get('processing_time_ms'),
    }


def make_postgres_sink(writer):
    """
    Factory: returns a sink(result, entry) callable bound to the given
    PostgresWriter, matching the signature worker.py's result_sinks expects.

    Args:
        writer (PostgresWriter): An already-connected writer instance.

    Returns:
        callable: sink(result, entry) -> None
    """
    def _sink(result, entry):
        row = _build_row(result, entry)
        writer.write(row)
    return _sink