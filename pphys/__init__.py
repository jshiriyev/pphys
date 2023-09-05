import os,sys,json

filedir = os.path.dirname(__file__)

filepath = os.path.join(filedir,"_pphys.json")

with open(filepath,"r") as jsonfile:
    library = json.load(jsonfile)

from dataclasses import dataclass

import numpy

from ._lasbrief import NanView
from ._lasbrief import TableView

from ._lasbatch import LasBatch

from ._bulkmodel import BulkModel

from ._depthview import DepthView
from ._depthview import DepthViewLasio #must be depreciated later once I fully prepare las file reader

from ._corrview import CorrView

from . import logan
# from . import corean

@dataclass
class archie:
    """It is the implementation of Archie's equation."""
    a  : float = 1.00 # tortuosity constant
    m  : float = 2.00 # cementation exponent
    n  : float = 2.00 # saturation exponent

    def ff(self,porosity):
        """Calculates formation factor based on Archie's equation."""
        return self.a/(porosity**self.m)

    def swn(self,porosity,rwater,rtotal):
        """Calculates water saturation to the power n based on Archie's equation."""
        return self.ff(porosity)*rwater/rtotal

    def sw(self,porosity,rwater,rtotal):
        """Calculates water saturation based on Archie's equation."""
        return numpy.power(self.swn(porosity,rwater,rtotal),1/self.n)

    @property
    def formation_factor(self):
        return self.ff

    @property
    def water_saturation_to_n(self):
        return self.swn
    
    @property
    def water_saturation(self):
        return self.sw
    