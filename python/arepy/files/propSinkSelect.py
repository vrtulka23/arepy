import numpy as np
import arepy as apy

class propSinkSelect:
    """Sink particle selectors

    Selector function specific for the sink particle properties only accessible in the sink particle snapshot.
    """

    def prop_SelectFormationOrder(self,ids,ptype,**prop):
        """Selecting particles with a given formation order values
        
        :param list[int] forder: List of formation order values
        :return: Particle selection indexes
        :rtype: list[bool]
        """
        idsSelect = np.in1d(self.prop_SinkFormationOrder(ids,ptype,**prop),prop['forder'])
        ids = np.where(ids, idsSelect, False)
        return self.getProperty(prop['p'],ids=ids,ptype=ptype) if 'p' in prop else ids
