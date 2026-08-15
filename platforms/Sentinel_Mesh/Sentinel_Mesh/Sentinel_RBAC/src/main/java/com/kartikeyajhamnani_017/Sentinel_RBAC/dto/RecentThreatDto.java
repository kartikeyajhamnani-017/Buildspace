package com.kartikeyajhamnani_017.Sentinel_RBAC.dto;


import java.time.OffsetDateTime;

/**
 * Maps to the `recent_threats` Postgres view for fast dashboard table rendering.
 */
public interface RecentThreatDto {
    Long getId();
    String getSourceIp();
    String getRequestType();
    String getPayload();
    Float getConfidence();
    String getThreatLevel();
    String getDetectionLayer();
    String getAttackType();
    String getDetectedAs();
    String getRouting();
    String getMitreAttack();
    OffsetDateTime getProcessedAt();
}