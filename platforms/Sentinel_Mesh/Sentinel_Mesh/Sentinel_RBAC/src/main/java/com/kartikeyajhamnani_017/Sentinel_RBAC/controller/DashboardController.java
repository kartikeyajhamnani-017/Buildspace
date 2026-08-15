package com.kartikeyajhamnani_017.Sentinel_RBAC.controller;

import com.kartikeyajhamnani_017.Sentinel_RBAC.dto.DashboardSummaryDto;
import com.kartikeyajhamnani_017.Sentinel_RBAC.dto.RecentThreatDto;
import com.kartikeyajhamnani_017.Sentinel_RBAC.service.DashboardService;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping("/dashboard")
    public String viewDashboard(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            Model model) {

        // 1. Fetch the paginated slice of recent threats natively from the Postgres View
        Page<RecentThreatDto> threatPage = dashboardService.getThreatDataFeed(page, size);

        // 2. Fetch the rich pipeline metrics (calculated natively by Postgres, no cache needed)
        DashboardSummaryDto metrics = dashboardService.getPipelineMetrics();

        // 3. Bind the paginated data table list
        model.addAttribute("threats", threatPage.getContent());
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", threatPage.getTotalPages());
        model.addAttribute("totalElements", threatPage.getTotalElements());

        // 4. Bind the new ML Engine metrics object
        model.addAttribute("metrics", metrics);

        // 5. Return the name of the Thymeleaf template (src/main/resources/templates/dashboard.html)
        return "dashboard";
    }
}