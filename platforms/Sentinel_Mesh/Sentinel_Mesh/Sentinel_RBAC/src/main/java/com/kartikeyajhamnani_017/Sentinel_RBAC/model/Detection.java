package com.kartikeyajhamnani_017.Sentinel_RBAC.model;




import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.OffsetDateTime;
import java.util.List;

@Entity
@Table(name = "detections")
public class Detection {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "source_ip", nullable = false, length = 45)
    private String sourceIp;

    @Column(name = "ingestor_timestamp")
    private OffsetDateTime ingestorTimestamp;

    @Column(name = "request_type", nullable = false, length = 10)
    private String requestType;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String payload;

    @Column(name = "is_malicious", nullable = false)
    private Boolean isMalicious;

    @Column(nullable = false)
    private Float confidence;

    @Column(name = "threat_level", nullable = false, length = 20)
    private String threatLevel;

    @Column(name = "detection_layer", nullable = false, length = 50)
    private String detectionLayer;

    @Column(name = "attack_type", length = 100)
    private String attackType;

    @Column(name = "matched_rule", columnDefinition = "TEXT")
    private String matchedRule;

    @Column(name = "anomaly_score")
    private Float anomalyScore;

    @Column(name = "detected_as", length = 10)
    private String detectedAs;

    @Column(length = 20)
    private String routing;

    @Column(name = "routing_note", columnDefinition = "TEXT")
    private String routingNote;

    // NATIVE HIBERNATE 6 JSONB SUPPORT
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "sequence_features", columnDefinition = "jsonb")
    private String sequenceFeatures;

    // NATIVE HIBERNATE 6 ARRAY SUPPORT
    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(name = "mitre_attack", columnDefinition = "text[]")
    private List<String> mitreAttack;

    @Column(name = "processing_time_ms")
    private Float processingTimeMs;

    @Column(name = "processed_at", nullable = false, updatable = false)
    private OffsetDateTime processedAt;

    // --- Constructors ---
    public Detection() {}

    // --- Getters and Setters ---
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getSourceIp() { return sourceIp; }
    public void setSourceIp(String sourceIp) { this.sourceIp = sourceIp; }

    public OffsetDateTime getIngestorTimestamp() { return ingestorTimestamp; }
    public void setIngestorTimestamp(OffsetDateTime ingestorTimestamp) { this.ingestorTimestamp = ingestorTimestamp; }

    public String getRequestType() { return requestType; }
    public void setRequestType(String requestType) { this.requestType = requestType; }

    public String getPayload() { return payload; }
    public void setPayload(String payload) { this.payload = payload; }

    public Boolean getIsMalicious() { return isMalicious; }
    public void setIsMalicious(Boolean malicious) { isMalicious = malicious; }

    public Float getConfidence() { return confidence; }
    public void setConfidence(Float confidence) { this.confidence = confidence; }

    public String getThreatLevel() { return threatLevel; }
    public void setThreatLevel(String threatLevel) { this.threatLevel = threatLevel; }

    public String getDetectionLayer() { return detectionLayer; }
    public void setDetectionLayer(String detectionLayer) { this.detectionLayer = detectionLayer; }

    public String getAttackType() { return attackType; }
    public void setAttackType(String attackType) { this.attackType = attackType; }

    public String getMatchedRule() { return matchedRule; }
    public void setMatchedRule(String matchedRule) { this.matchedRule = matchedRule; }

    public Float getAnomalyScore() { return anomalyScore; }
    public void setAnomalyScore(Float anomalyScore) { this.anomalyScore = anomalyScore; }

    public String getDetectedAs() { return detectedAs; }
    public void setDetectedAs(String detectedAs) { this.detectedAs = detectedAs; }

    public String getRouting() { return routing; }
    public void setRouting(String routing) { this.routing = routing; }

    public String getRoutingNote() { return routingNote; }
    public void setRoutingNote(String routingNote) { this.routingNote = routingNote; }

    public String getSequenceFeatures() { return sequenceFeatures; }
    public void setSequenceFeatures(String sequenceFeatures) { this.sequenceFeatures = sequenceFeatures; }

    public List<String> getMitreAttack() { return mitreAttack; }
    public void setMitreAttack(List<String> mitreAttack) { this.mitreAttack = mitreAttack; }

    public Float getProcessingTimeMs() { return processingTimeMs; }
    public void setProcessingTimeMs(Float processingTimeMs) { this.processingTimeMs = processingTimeMs; }

    public OffsetDateTime getProcessedAt() { return processedAt; }
    public void setProcessedAt(OffsetDateTime processedAt) { this.processedAt = processedAt; }
}