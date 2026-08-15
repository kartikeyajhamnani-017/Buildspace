package com.kartikeyajhamnani_017.Sentinel_RBAC.service;




import com.kartikeyajhamnani_017.Sentinel_RBAC.dto.DashboardSummaryDto;
import com.kartikeyajhamnani_017.Sentinel_RBAC.dto.RecentThreatDto;
import com.kartikeyajhamnani_017.Sentinel_RBAC.repository.DetectionRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

@Service
public class DashboardService {

    private final DetectionRepository detectionRepository;

    public DashboardService(DetectionRepository detectionRepository) {
        this.detectionRepository = detectionRepository;
    }

    public Page<RecentThreatDto> getThreatDataFeed(int page, int size) {
        int safeSize = Math.min(size, 100);
        // We no longer need to pass Sort here; the `recent_threats` view handles ORDER BY
        return detectionRepository.findRecentThreatsNatively(PageRequest.of(page, safeSize));
    }

    public DashboardSummaryDto getPipelineMetrics() {
        // Hits the DB View directly - no caching required!
        return detectionRepository.getGlobalSummary();
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'SOC_ANALYST')")
    public void markAsFalsePositive(Long detectionId) {
        // Example action: Find detection, flip isMalicious to false, save.
    }
}