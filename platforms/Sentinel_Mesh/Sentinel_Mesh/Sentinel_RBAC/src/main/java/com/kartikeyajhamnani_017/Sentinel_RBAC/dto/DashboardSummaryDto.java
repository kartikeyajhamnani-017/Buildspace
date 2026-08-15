package com.kartikeyajhamnani_017.Sentinel_RBAC.dto;



import java.time.OffsetDateTime;

/**
 * Maps exactly to the columns returned by the `detection_summary` Postgres view.
 */
public interface DashboardSummaryDto {
    Long getTotalProcessed();
    Long getTotalThreats();
    Long getLayer1Hits();
    Long getLayer2Hits();
    Long getLayer3Hits();
    Long getRoutingDisagreements();
    OffsetDateTime getLastProcessedAt();
}
