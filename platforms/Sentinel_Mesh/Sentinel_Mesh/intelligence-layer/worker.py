
"""
Sentinel ML Engine v2.0 - Redis Queue Consumer (Worker)
Connects the Go ingestor's Redis queue to the Python intelligence layer.

Architecture:
    Go Ingestor --RPUSH--> Redis "traffic_queue" --BLPOP--> this worker
                                                                  |
                                                            SentinelMLEngine.analyze()
                                                                  |
                                                            result_sink(result, entry)

Message format pushed by the Go ingestor (see main.go LogEntry struct):
    {
        "source_ip":    "10.0.0.5",
        "timestamp":    "2026-06-16T12:00:00Z",
        "payload":      "admin' OR '1'='1'--",
        "request_type": "HTTP"
    }

Delivery semantics: the underlying queue is a plain Redis list (RPUSH/BLPOP),
which is at-most-once delivery. If this worker crashes after popping a
message but before processing finishes, that message is lost — there is
no redelivery. Acceptable for now; if that risk becomes unacceptable,
migrate the queue to Redis Streams with a consumer group for at-least-once
delivery and replay support. Nothing in this file would need to change at
the SentinelMLEngine boundary, only _pop_one()'s implementation.
"""

import json
import signal
import sys
import time
import argparse
import logging

import redis

from main import SentinelMLEngine
import config


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger('sentinel.worker')


# ==============================================================================
# RESULT SINKS  (pluggable — swap in a Postgres writer later without
# touching the consumer loop itself)
# ==============================================================================

def console_sink(result, entry):
    """Default sink: log the result to stdout. Replace with a Postgres
    writer once that's built — same function signature, same call site."""
    tag = "THREAT" if result['is_malicious'] else "clean"
    logger.info(
        "[%s] ip=%s protocol=%s layer=%s confidence=%.2f payload=%r",
        tag,
        entry.get('source_ip', 'unknown'),
        entry.get('request_type', 'HTTP'),
        result['detection_layer'],
        result['confidence'],
        entry.get('payload', '')[:80],
    )


def jsonl_file_sink(filepath):
    """
    Factory: returns a sink that appends each result as one JSON line to
    a file. Useful as an immediate durable log before Postgres exists.
    """
    def _sink(result, entry):
        record = {
            'source_ip':         entry.get('source_ip', 'unknown'),
            'ingestor_timestamp': entry.get('timestamp'),
            'request_type':      entry.get('request_type', 'HTTP'),
            'payload':           entry.get('payload', ''),
            'is_malicious':      result['is_malicious'],
            'confidence':        result['confidence'],
            'threat_level':      result['threat_level'],
            'detection_layer':   result['detection_layer'],
            'attack_type':       result.get('attack_type'),
            'detected_as':       result.get('detected_as'),
            'routing':           result.get('routing'),
            'mitre_attack':      result.get('mitre_attack'),
            'processing_time_ms': result.get('processing_time_ms'),
            'processed_at':      time.time(),
        }
        with open(filepath, 'a') as f:
            f.write(json.dumps(record) + '\n')
    return _sink


# ==============================================================================
# CONSUMER
# ==============================================================================

class RedisQueueConsumer:
    """
    Pulls payload entries off the Go ingestor's Redis list and routes
    them through SentinelMLEngine. One instance == one worker process.
    Multiple instances can run concurrently against the same queue —
    BLPOP is atomic per item, so Redis distributes items across workers
    without duplication.
    """

    QUEUE_KEY = 'traffic_queue'

    def __init__(self, engine, redis_client, result_sinks=None,
                 block_timeout=5, stats_interval=100):
        """
        Args:
            engine          (SentinelMLEngine): Initialized detection engine.
            redis_client    (redis.Redis):       Dedicated client for BLPOP.
                                                  Kept separate from the engine's
                                                  internal sequence-tracking client
                                                  to avoid blocking it.
            result_sinks    (list[callable]):    Functions called as
                                                  sink(result, entry) for every
                                                  processed message. Defaults to
                                                  [console_sink].
            block_timeout   (int):  Seconds BLPOP waits before returning None,
                                     allowing the loop to check for shutdown.
            stats_interval  (int):  Log throughput stats every N messages.
        """
        self.engine         = engine
        self.redis_client   = redis_client
        self.result_sinks   = result_sinks or [console_sink]
        self.block_timeout  = block_timeout
        self.stats_interval = stats_interval

        self._running        = False
        self._processed_count = 0
        self._threat_count    = 0
        self._error_count     = 0
        self._start_time       = None

    def run(self):
        """Start the blocking consume loop. Runs until stop() is called
        or a termination signal is received."""
        self._running   = True
        self._start_time = time.time()

        logger.info("Worker started — listening on Redis list '%s'", self.QUEUE_KEY)

        while self._running:
            entry = self._pop_one()
            if entry is None:
                continue  # timed out waiting, loop again to check _running

            self._process_entry(entry)

            if self._processed_count % self.stats_interval == 0:
                self._log_stats()

        self._log_stats(final=True)
        logger.info("Worker stopped cleanly.")

    def stop(self):
        """Signal the run loop to exit after the current blocking call returns."""
        self._running = False

    # ── Internals ──────────────────────────────────────────────────────────────

    def _pop_one(self):
        """
        Block up to block_timeout seconds for one message.
        Returns the parsed entry dict, or None on timeout/parse failure.
        """
        try:
            result = self.redis_client.blpop(self.QUEUE_KEY, timeout=self.block_timeout)
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis connection error: %s — retrying in 2s", e)
            time.sleep(2)
            return None

        if result is None:
            return None  # timeout, no message — normal, allows shutdown checks

        _, raw_value = result

        try:
            entry = json.loads(raw_value)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Malformed message dropped: %s — raw=%r", e, raw_value[:200])
            self._error_count += 1
            return None

        return entry

    def _process_entry(self, entry):
        """Map the Go ingestor's field names to analyze() args, run detection,
        dispatch to all configured result sinks."""
        payload  = entry.get('payload', '')
        ip       = entry.get('source_ip', 'unknown')
        protocol = (entry.get('request_type') or 'HTTP').upper().strip()

        if not payload:
            logger.warning("Empty payload, skipping entry: %r", entry)
            self._error_count += 1
            return

        try:
            result = self.engine.analyze(payload, ip_address=ip, protocol=protocol)
        except Exception as e:
            logger.error("analyze() failed for entry %r: %s", entry, e)
            self._error_count += 1
            return

        self._processed_count += 1
        if result['is_malicious']:
            self._threat_count += 1

        for sink in self.result_sinks:
            try:
                sink(result, entry)
            except Exception as e:
                logger.error("Result sink %s failed: %s", getattr(sink, '__name__', sink), e)

    def _log_stats(self, final=False):
        elapsed   = time.time() - self._start_time if self._start_time else 0
        rate      = self._processed_count / elapsed if elapsed > 0 else 0
        try:
            queue_depth = self.redis_client.llen(self.QUEUE_KEY)
        except Exception:
            queue_depth = '?'

        label = "FINAL STATS" if final else "stats"
        logger.info(
            "[%s] processed=%d threats=%d errors=%d rate=%.1f/s queue_depth=%s",
            label, self._processed_count, self._threat_count,
            self._error_count, rate, queue_depth,
        )


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def _build_redis_client():
    """Dedicated Redis client for the blocking consume loop — kept separate
    from the engine's internal sequence-tracking client."""
    return redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        decode_responses=True,
    )


def main():
    parser = argparse.ArgumentParser(description='Sentinel ML Engine v2.0 — Redis Queue Worker')
    parser.add_argument('--log-file', help='Also append results as JSONL to this file')
    parser.add_argument('--postgres-dsn',
                         help='Postgres connection string, e.g. '
                              'postgresql://sentinel:sentinel@localhost:5432/sentinel_db. '
                              'If omitted, results are not persisted to Postgres.')
    parser.add_argument('--block-timeout', type=int, default=5,
                         help='Seconds BLPOP waits before checking for shutdown (default: 5)')
    parser.add_argument('--stats-interval', type=int, default=100,
                         help='Log throughput stats every N processed messages (default: 100)')
    args = parser.parse_args()

    engine = SentinelMLEngine(use_redis=True)

    consumer_redis = _build_redis_client()
    try:
        consumer_redis.ping()
    except redis.exceptions.ConnectionError as e:
        logger.error("Cannot reach Redis at %s:%s — %s", config.REDIS_HOST, config.REDIS_PORT, e)
        sys.exit(1)

    sinks = [console_sink]
    if args.log_file:
        sinks.append(jsonl_file_sink(args.log_file))
        logger.info("Also logging results to %s", args.log_file)

    if args.postgres_dsn:
        # Imported lazily so psycopg2 is only required when --postgres-dsn
        # is actually used — the worker still runs fine without Postgres.
        from postgres_sink import PostgresWriter, make_postgres_sink
        try:
            writer = PostgresWriter(dsn=args.postgres_dsn)
            sinks.append(make_postgres_sink(writer))
            logger.info("Also persisting results to Postgres.")
        except Exception as e:
            logger.error("Could not connect to Postgres at startup: %s", e)
            logger.error("Continuing without Postgres persistence — fix the DSN and restart to enable it.")

    consumer = RedisQueueConsumer(
        engine=engine,
        redis_client=consumer_redis,
        result_sinks=sinks,
        block_timeout=args.block_timeout,
        stats_interval=args.stats_interval,
    )

    def _handle_shutdown(signum, frame):
        logger.info("Received signal %s — shutting down gracefully...", signum)
        consumer.stop()

    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    consumer.run()


if __name__ == '__main__':
    main()