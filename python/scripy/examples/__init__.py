import arepy as apy

class project(apy.scripy.project):

    def init(self):
        
        # Simulation directory of a project
        # This variable need to stay defined !!!
        self.dirSim = "/home/hd/hd_hd/hd_wd148/wsexamples"

        # Setup of a new simulation
        self.sims['001'] = {
            'dir': self.dirSim+'/subdirectory',
            'name':'first','setup':'first',
            'job':{'nodes':1,'proc':40,'time':'1:00:00','type':'fat'},
            'units':{'length':apy.const.pc,'time':apy.const.yr},
            'opt':{}
        }
