# -*- coding: utf-8 -*-

"""
 Etiquetas in Bbx define some behaviours of the system, beside qualifying
 contents. Each etiqueta can be associated to a set of policies
 (TRIAGE_DIR). 

 Actually policies will be linked to Django Signals selected by name. For
 example, a policy called "postSave_copyToTaina" is imported and executed
 on post save signals.

 TODO: O arquivo  na real contem a função mesmo.. não precisa de
       json. As etiquetas periodicamenta vão ser definidas e carregada
       com as fixtures.

"""

from django.db import models
from bbx.settings import POLICIES_DIR, TRIAGE_DIR
from bbx.utils import MultiSelectField
import json
import os
import exceptions

# This is to specify to south how to work with MultiSelectField:
# http://south.readthedocs.org/en/latest/customfields.html
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["bbx.utils.MultiSelectField"])


class PoliciesPersistentDataUnavailable(exceptions.Exception):
    def __init__(self,args=None):
        self.args = args

def getAvailablePolicies():
    """Get a list of available policies from TRIAGE_DIR."""
    policiesList = [( os.path.splitext(name)[0], os.path.splitext(name)[0]) \
                        for name in os.listdir(TRIAGE_DIR) if name.endswith(".py") \
                        if not (name.startswith("__")) ]
    return policiesList
   
class Etiqueta(models.Model):
    namespace = models.CharField(max_length=10, blank=True, default='')
    note = models.TextField(max_length=300, blank=True)
    etiqueta = models.CharField(max_length=26)
    policies = MultiSelectField(max_length=100, choices=getAvailablePolicies(), blank=True)

    def __unicode__(self):
        return self.namespace + ":" + self.etiqueta if self.namespace != '' else self.etiqueta 

    def getId(self):
        """
        Returns etiqueta's id built as namespace + etiqueta, ex.:
        bbx:publico ("etiqueta" attribute shoul'd be "name" FIX:
        rename!)
        
        """
        return self.namespace + ":" + self.etiqueta if self.namespace != '' else self.etiqueta 

    def _getPoliciesFilename(self):
        """
        Policies file is built with POLICIES_DIR and etiqueta's id
        
        """
        return POLICIES_DIR +'/'+ self.getId() + '.json'

    def setNamespace(self):
        """
        Sets etiqueta's namespace like in bbx:publico gets "bbx" :)
        
        """
        if self.etiqueta.find(':') > 0:
            args = self.etiqueta.split(':')
            self.namespace = args[0]

    def setEtiqueta(self):
        """
        Sets etiqueta's name. FIX
        
        """
        if self.etiqueta.find(':') > 0:
            args = self.etiqueta.split(':')
            self.etiqueta = args[1]

    def save(self, *args, **kwargs):
        """
        Save also etiqueta's policies to a JSON file.
        
        """

        self.setNamespace()
        self.setEtiqueta()
        super(Etiqueta, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('etiqueta',)
        unique_together = ("namespace", "etiqueta")
