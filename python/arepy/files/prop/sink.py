import numpy as np
import arepy as apy

class sink:
    """Properties of the sink particle file

    Propertis in this class are extracted from the sink particle snapshot files.
    Therefore, they are accessible only if the sink particle snapshot are available.
    It is possible to call sink snapshot properties when particle type is set to ptype=5.
    """

    def prop_SinkFormationOrder(self,ids,ptype,**prop):
        """Returns value of the sink formation order

        :return: Formation order of sink particles
        :rtype: list[int]
        """
        return self.getSinkData('FormationOrder',ids)

    def prop_SinkFormationTime(self,ids,ptype,**prop):
        """Returns value of the sink formation time

        :return: Formation time of sink particles
        :rtype: list[float]
        """
        return self.getSinkData('FormationTime',ids)

    def prop_SinkID(self,ids,ptype,**prop):
        """Returns value of the sink IDs

        :return: Particle IDs of sink particles
        :rtype: list[int]
        """
        return self.getSinkData('ID',ids)

    def prop_SinkPos(self,ids,ptype,**prop):
        """Returns sink particle coordinates from the sink snapshot

        :return: Sink particle coordinates
        :rtype: list[[int]*3]
        """
        return self.getSinkData('Pos',ids)

    def prop_SinkAge(self,ids,ptype,**prop):
        """Returns ages of the sink particles

        :return: Ages of sink particles
        :rtype: list[float]
        """
        return self.snapTime - self.prop_SinkFormationTime(ids,ptype,**prop)

    def prop_SinkMass(self,ids,ptype,**prop):
        """Returns value of the sink masses

        :return: Masses of sink particles
        :rtype: list[float]
        """
        return self.getSinkData('Mass',ids)

    def prop_SinkMassOld(self,ids,ptype,**prop):
        """Returns value of the sink masses at the last SPRAI run

        :return: Masses of sink particles
        :rtype: list[float]
        """
        return self.getSinkData('MassOld',ids)

    def prop_SinkAccretionRate(self,ids,ptype,**prop):
        """Returns value of the sink accretion rate

        :return: Accretion rate of sink particles
        :rtype: list[float]
        """
        return self.getSinkData('AccretionRate',ids)
