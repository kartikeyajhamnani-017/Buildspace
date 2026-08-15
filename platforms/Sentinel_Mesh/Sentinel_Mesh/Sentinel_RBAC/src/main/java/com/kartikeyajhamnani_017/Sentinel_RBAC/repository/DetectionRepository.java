package com.kartikeyajhamnani_017.Sentinel_RBAC.repository;




import com.kartikeyajhamnani_017.Sentinel_RBAC.dto.DashboardSummaryDto;
import com.kartikeyajhamnani_017.Sentinel_RBAC.dto.RecentThreatDto;
import com.kartikeyajhamnani_017.Sentinel_RBAC.model.Detection;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface DetectionRepository extends JpaRepository<Detection, Long> {

    // 1. Query the View natively for the data table
    // mitre_attack is text[] in the view; flattened to a comma-separated string here
    // so it maps cleanly onto a plain String getter in the projection interface.
    @Query(value = "SELECT id, source_ip, request_type, payload, confidence, threat_level, " +
            "detection_layer, attack_type, detected_as, routing, " +
            "array_to_string(mitre_attack, ', ') AS mitre_attack, processed_at " +
            "FROM recent_threats",
            countQuery = "SELECT count(*) FROM recent_threats",
            nativeQuery = true)
    Page<RecentThreatDto> findRecentThreatsNatively(Pageable pageable);

    // 2. Query the summary View for the top metric cards
    @Query(value = "SELECT * FROM detection_summary", nativeQuery = true)
    DashboardSummaryDto getGlobalSummary();
}
