package com.kartikeyajhamnani_017.Internal_flag_manager.controller;

import com.kartikeyajhamnani_017.Internal_flag_manager.model.Features;
import com.kartikeyajhamnani_017.Internal_flag_manager.service.Featureservice;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.ui.Model;



@Controller
public class DashboardController {
    @Autowired
    private Featureservice featureservice ;

    @GetMapping("/")
    public String showdashboard(Model model){
        model.addAttribute("features", featureservice.getallfeatures());
        return "index" ;
    }

    // --- 1. MAPPING FOR THE "CREATE" FORM ---
    // This matches: <form th:action="@{/create}" method="post">
    @PostMapping("/create")
    public String createFeature(Features feature) {
        featureservice.savefeature(feature);
        return "redirect:/"; // Reload the homepage
    }

    // --- 2. MAPPING FOR THE "TOGGLE" FORM ---
    // This matches: <form th:action="@{/toggle/{id}(id=${feature.id})}" method="post">
    @PostMapping("/toggle/{id}")
    public String toggleFeature(@PathVariable Long id) {
        featureservice.togglestatus(id);
        return "redirect:/"; // Reload the homepage
    }

    // --- 3. MAPPING FOR THE "DELETE" FORM ---
    // This matches: <form th:action="@{/delete/{id}(id=${feature.id})}" method="post">
    @PostMapping("/delete/{id}")
    public String deleteFeature(@PathVariable Long id) {
        featureservice.deletefeature(id);
        return "redirect:/"; // Reload the homepage
    }

}
