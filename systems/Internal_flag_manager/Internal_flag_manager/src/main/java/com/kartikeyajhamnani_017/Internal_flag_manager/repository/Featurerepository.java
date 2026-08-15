package com.kartikeyajhamnani_017.Internal_flag_manager.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.kartikeyajhamnani_017.Internal_flag_manager.model.Features;


@Repository
public interface Featurerepository extends JpaRepository<Features,Long> {
}
