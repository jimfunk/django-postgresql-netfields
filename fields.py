from django.db import models                                                  
                                                                                                           
class IPAddressField(models.IPAddressField):                                                               
    def get_db_prep_lookup(self, lookup_type, value):                                                      
        if lookup_type.startswith('inet_'):                                                                
            return [value]                                                    
        return super(IPAddressField, self).get_db_prep_lookup(lookup_type, value) 