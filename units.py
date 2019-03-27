import numpy as np
import arepy as apy
import os

# Create unit conversion constants
class units():
    def __init__(self,old=None,new=None):
        
        self.names = ['mass','length','velocity','density','volume','energy','time','a','h','numdens','flux']

        self.conv = {}
        for name in self.names:
            self.conv[name] = 1.
        
        if old is not None:
            self.setOld(old)
        if new is not None:
            self.setNew(new)

    def getUnitSystem(self,system):
        if system=='cgs':
            return {'mass':1.,'length':1.,'velocity':1.}
        elif system=='si':
            return {'mass':1e3,'lenght':1e2,'velocity':1e2}
            
    def setOld(self,units):

        if isinstance(units,str):
            units = self.getUnitSystem(units)

        # Setup default units
        self.old = {'mass':apy.const.M_sol,'length':apy.const.pc}
        for key in units.keys():
            self.old[key] = units[key]            
        if 'velocity' not in self.old and 'time' in self.old:
            self.old['velocity'] = self.old['length'] / self.old['time']
        elif 'velocity' in self.old and 'time' not in self.old:
            self.old['time'] = self.old['length'] / self.old['velocity']
        elif 'velocity' not in self.old and 'time' not in self.old:
            self.old['time'] = apy.const.yr
            self.old['velocity'] = self.old['length'] / self.old['time']

        # Setup derived units
        if 'density' not in self.old:
            self.old["density"]    = self.old["mass"] / self.old["length"]**3
        if 'volume' not in self.old:
            self.old['volume']     = self.old['length']**3
        if 'energy' not in self.old:
            self.old["energy"]     = self.old["velocity"]**2     # internal energy E/m=v^2=(m/s)^2
        if 'flux' not in self.old or self.old['flux'] is None:
            self.old['flux'] = 1.
        if 'numdens' not in self.old:
            self.old['numdens']    = 1./self.old['length']**3

        # Setup cosmological units
        if 'h' not in self.old:
            self.old['h'] = 1.0
        if 'a' not in self.old:
            self.old['a'] = 1.0

    def setNew(self,units):

        if isinstance(units,str):
            units = self.getUnitSystem(units)

        self.new = {}
        if units is not None:
            for key in units.keys():
                self.new[key] = units[key]
            
        if 'length' not in self.new:
            self.new['length']     = self.old['length']
        if 'mass' not in self.new:
            self.new['mass']       = self.old['mass']
        if 'velocity' not in self.new:
            self.new['velocity']   = self.old['velocity']

        if 'density' not in self.new:
            self.new["density"]    = self.new["mass"] / self.new["length"]**3
        if 'volume' not in self.new:
            self.new['volume']     = self.new['length']**3
        if 'energy' not in self.new:
            self.new["energy"]     = self.new["velocity"]**2     # internal energy E/m=v^2=(m/s)^2
        if 'time' not in self.new:
            self.new['time']       = self.new['length'] / self.new['velocity']
        
        if 'numdens' not in self.new:
            self.new['numdens']    = 1.    # we want this to stay in cm^-3
        if 'flux' not in self.new:
            self.new['flux']       = 1.    # we want to have always units of ph/s

        if 'h' not in self.new:
            self.new['h']     = self.old['h']
        if 'a' not in self.new:
            self.new['a']     = self.old['a']

        cosmoConv = {
            'length':   (self.old['a']/self.old['h']) / (self.new['a']/self.new['h']),
            'mass':     (1.0/self.old['h']) / (1.0/self.new['h']),
            'velocity': np.sqrt( self.old['a'] / self.new['a'] ),
            'density':  (self.old['h']**2/self.old['a']**3) / (self.new['h']**2/self.new['a']**3),
            'volume':   ((self.old['a']/self.old['h']) / (self.new['a']/self.new['h']))**3,
            'energy':   1.0,
            'time':     1.0,
            'numdens':  (self.new['a']/self.new['h'])**3 / (self.old['a']/self.old['h'])**3,
            'flux':     1.0,
            }

        self.conv = {}
        convUnits = ['length','mass','velocity','density','volume','energy','time','numdens','flux']
        for unit in convUnits:
            self.conv[unit] = self.old[unit] / self.new[unit] * cosmoConv[unit]
        self.conv['a'] = self.old['a'] / self.new['a']
        self.conv['h'] = self.old['h'] / self.new['h']

    def show(self):
        tbl = apy.data.table()
        tbl.column('unit name',self.names)
        tbl.column('old value',[self.old[name] for name in self.names])
        tbl.column('new value',[self.new[name] for name in self.names])
        tbl.column('conv',[self.conv[name] for name in self.names])
        tbl.column('old unit',[self.guess(name,'old') for name in self.names])
        tbl.column('new unit',[self.guess(name,'new') for name in self.names])
        tbl.show()

    def guess(self,name,value=1.,utype='old',umin=None,umax=None,nformat='%.1f'):
        nformat = nformat+' %s'
        if name=='length':
            unitNames = ['cm','km','au','pc','kpc','Mpc','Gpc','inf']
            unitValues = [1, 100, apy.const.au, apy.const.pc, apy.const.kpc, 
                      apy.const.Mpc, apy.const.Gpc, float("inf")]
        elif name=='time':
            unitNames = ['s','m','h','d','yr','kyr','Myr','Gyr','inf']
            unitValues = [1, 60, 3600, 86400, apy.const.yr, apy.const.kyr, 
                          apy.const.Myr, apy.const.Gyr, float("inf")]
        elif name=='mass': 
            unitNames = ['g','kg','mM_sol','M_sol','inf']
            unitValues = [1, 1e3, apy.const.M_sol*1e-3, apy.const.M_sol, float("inf")]
        if name in ['length','time','mass']:
            if utype=='old': value *= self.old[name]
            elif utype=='new': value *= self.new[name]
            umin = 0 if umin is None else unitNames.index(umin)
            umax = len(unitNames)-1 if umax is None else unitNames.index(umax)
            for i in range(umin,umax):
                if unitValues[i+1]>=value*2: # "value*2" is to avoid small rounding differences
                    return nformat%(value/unitValues[i], unitNames[i])
            return nformat%(value/unitValues[umax], unitNames[umax])
        else:
            return ''
        
    def __getitem__(self, unit):
        return self.old[unit]
