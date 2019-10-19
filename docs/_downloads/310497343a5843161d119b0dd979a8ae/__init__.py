import arepy as apy

class project(apy.scripy.project):
    """Project class 'example'

    This project class inherits :class:`arepy.scripy.project` class.
    """

    def init(self):
        """Project initialization

        This method should include initial settings of all simulations within the project.

        A default simulation directory should be set here:
        
        .. literalinclude:: ../../python/scripy/examples/__init__.py
            :language: python
            :lines: 27

        A first simulation called '001' is set in a following way:

        .. literalinclude:: ../../python/scripy/examples/__init__.py
            :language: python
            :lines: 29-34
        """

        self.dirSim = apy.dirHome+"/wsexamples"

        self.sims['001'] = {
            'name':'hiiregion','setup':'emptybox',
            'job':{'nodes':1,'proc':40,'time':'1:00:00','type':'fat'},
            'units':{'length':apy.const.pc,'time':apy.const.yr},
            'opt':{}
        }
