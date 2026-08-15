package com.kartikeyajhamnani_017.Internal_flag_manager.controller;
import java.lang.*;
import java.util.List;
import com.kartikeyajhamnani_017.Internal_flag_manager.service.Featureservice;
import com.kartikeyajhamnani_017.Internal_flag_manager.model.Features;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/feature")
public class Featurecontroller {
    @Autowired
    private Featureservice featureservice ;

    @PostMapping("/add")
    public String add (@RequestBody Features feature){
        featureservice.savefeature(feature);
        return "New feature added ";
    }

    @GetMapping("/listall")
    public List<Features> getallfeatures(){
        return featureservice.getallfeatures();
    }

    @PutMapping("/toggle/{id}")
        public ResponseEntity<Features> togglefeaturestatus(@PathVariable Long id){
            Features updatedfeature = featureservice.togglestatus(id);

            return ResponseEntity.ok(updatedfeature);

        }


        @DeleteMapping("/delete/{id}")
       public ResponseEntity<Void> featuredelete(@PathVariable Long id){
        featureservice.deletefeature(id);

         return ResponseEntity.ok().build();
        }

    @DeleteMapping("/deleteall")
    public ResponseEntity<Void> featuredelete(){
        featureservice.deleteallfeature();

        return ResponseEntity.ok().build();
    }


    }


