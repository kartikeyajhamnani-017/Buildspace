package com.kartikeyajhamnani_017.Internal_flag_manager.service;
import java.lang.*;
import java.util.List;
import com.kartikeyajhamnani_017.Internal_flag_manager.model.Features;


public interface Featureservice {

    public Features savefeature(Features feature);
    public  List<Features> getallfeatures();
    public Features togglestatus(Long id);
    void  deletefeature(Long id);
    void deleteallfeature();
}
