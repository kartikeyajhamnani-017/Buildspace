package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ContactResponse {

    private Integer contactId;
    private String contactName;
    private String contactEmail;

}
