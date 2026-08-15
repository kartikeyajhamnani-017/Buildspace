package com.kartikeyajhamnani_017.Internal_flag_manager.service;

import java.util.List;
import com.kartikeyajhamnani_017.Internal_flag_manager.model.Features;
import com.kartikeyajhamnani_017.Internal_flag_manager.repository.Featurerepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class Featureserviceimpl implements Featureservice {


    @Autowired
    private Featurerepository featurerepository;

    @Override
    public Features savefeature(Features feature){
      return featurerepository.save(feature);
  };

    @Override
    public List<Features> getallfeatures() {
        return featurerepository.findAll();
    }

    @Transactional
    public Features togglestatus(Long id){
        Features feature = featurerepository.findById(id).orElseThrow(() -> new RuntimeException("Feature not found with id: " + id));
        feature.setActive(!feature.isActive());
        return featurerepository.save(feature);

    }

    @Override
    @Transactional
    public void deletefeature(Long id) {
        if (!featurerepository.existsById(id)){ throw new RuntimeException("Feature not found with id:" + id);}

        featurerepository.deleteById(id);
        }

    @Override
    @Transactional
    public void deleteallfeature() {

        featurerepository.deleteAll();

    }


}
