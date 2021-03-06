import h5py as hp
import numpy as np
import arepy as apy

# Cut snapshots
class cut():
    def __init__(self,sim,snap,cut,units):
        self.sim = sim
        self.snap = snap
        apy.shell.printc('Cutting simulation "%s"'%sim.name,'g')

        self.units = apy.units({
            'length':  sim.units['length'],
            'mass':    sim.units['mass'],
            'velocity':sim.units['velocity'],
        },units)
        print( 'Length:       %-15s -> %s'%(self.units.guess('length',utype='old'), self.units.guess('length',utype='new')) )
        print( 'Mass:         %-15s -> %s'%(self.units.guess('mass',utype='old'),   self.units.guess('mass',utype='new')) )
        print( 'Velocity:     %-15s -> %s'%(self.units.guess('time',utype='old'),   self.units.guess('time',utype='new')) )

        self.cut = cut             # in old units
        print( 'Cutting time: %-15s =  %s'%(self.cut['time'][0],self.units.guess('time',self.cut['time'][0],'old')) )
        print( 'New TimeMax:  %-15s =  %s'%(self.cut['time'][1],self.units.guess('time',self.cut['time'][1],'old')) )
        print( 'Coordinates:  ', self.cut['coord'] )

    def setupConfig(self,fileName,edit=False):
        apy.shell.printc('Cutting config file...','g')
        cf = apy.files.config()
        cf.read(self.sim.fileConfig)

        data = {}

        # change the boundary conditions
        if 'coord' in self.cut:
            data['REFLECTIVE_X'] = 2
            data['REFLECTIVE_Y'] = 2
            data['REFLECTIVE_Z'] = 2

        # custom config settings
        if edit!=False:
            edit(data,cf)

        print( "%-40s %-30s %s"%('Parameter','Old value', 'New value') )
        print( "%-40s %-30s %s"%('---------','---------', '---------') )
        for group in cf.groups:
            for key in group['params']:
                if key not in data: continue
                oldValue=cf.formatValue(key)
                newValue=cf.formatValue(key,data[key])
                print( "%-40s %-30s %s"%(key,oldValue, newValue) )

        for key,value in data.items():
            if cf.getDtype(key)=='e':
                cf.setValue(key,'')
            else:
                cf.setValue(key,value)

        cf.write(fileName)

    def setupParam(self,fileName,edit=False):
        apy.shell.printc('Cutting parameter file...','g')
        pf = apy.files.param()
        pf.read(self.sim.fileParam,notes=False)
        
        data = {}

        # conversion of units
        data['UnitLength_in_cm'] = self.units.new['length']
        data['UnitMass_in_g'] = self.units.new['mass']
        data['UnitVelocity_in_cm_per_s'] = self.units.new['velocity']
        
        # standard conversion parameters
        conversions = {
            'TimeBegin':'time','TimeMax':'time','MaxSizeTimestep':'time','MinSizeTimestep':'time',
            'TimeBetSnapshot':'time','TimeOfFirstSnapshot':'time','TimeBetStatistics':'time',
            'BoxSize':'length',
            'ReferenceGasPartMass':'mass',
            'SinkCreationDensityCodeUnits':'density', 'SinkFormationRadius':'length'
        }
        for key,conv in conversions.items():
            value = pf.getValue(key)
            if value!=None:
                data[key] = value * self.units.conv[conv]

        # conversions due to the box cutting
        if 'time' in self.cut:
            data['TimeBegin'] = 0.0
            data['TimeMax'] = self.cut['time'][1]*self.units.conv['time']
        if 'coord' in self.cut:
            data['BoxSize'] = (self.cut['coord'][1]-self.cut['coord'][0])*self.units.conv['length']
        
        # custom conversions 
        if edit!=False:
            edit(data,pf)

        print( "%-40s %-30s %s"%('Parameter', 'Old value', 'New value') )
        print( "%-40s %-30s %s"%('---------', '---------', '---------') )
        for group in pf.groups:
            for key in group['params']:
                if key in data:
                    print( "%-40s %-30s %s"%(key, pf.formatValue(key), pf.formatValue(key,data[key]) ) )

        for key,value in data.items():
            pf.setValue(key, value)

        pf.write(fileName)

    def setupSink(self,fileName,oldKwargs,newKwargs):
        apy.shell.printc('Cutting sink particle file...','g')
        apy.shell.printc('Please check the new sink file if the changes are really correct!','r')

        # create a new sink file
        nf = apy.files.sink('',**newKwargs)

        # cut old values and paste to new snap file 
        with apy.files.sink(self.sim.fileSink,**oldKwargs) as of:
            nf.snapTime = of.snapTime
            if 'time' in self.cut:
                nf.snapTime -= self.cut['time'][0]
            nf.snapTime *= self.units.conv['time']
            ids = self._cutCoords( of.getValues('Pos') )
            nf.nSinks = ids.sum()
            for prop in nf.propsOrder:
                value = of.getValues(prop)
                value = nf.getEmpty(prop) if value is None else value[ids]
                nf.setValues(prop, value)
            of.show(order='Mass',reverse=True,limit=10)

        # do additional adjustments to the values
        if 'coord' in self.cut:
            nf.setValues('Pos', nf.getValues('Pos') - self.cut['coord'][::2] )
        nf.setValues('Pos', nf.getValues('Pos') * self.units.conv['length'] )
        nf.setValues('Vel', ( nf.getValues('Vel') - self.cut['bulkVel'] ) * self.units.conv['velocity'] )
        nf.setValues('Mass', nf.getValues('Mass') * self.units.conv['mass'] )
        if 'simplex' in newKwargs:
            nf.setValues('MassOld', nf.getValues('Mass') * self.units.conv['mass'] ) # here we use the actual mass
        if 'varAccRad' in newKwargs:
            nf.setValues('AccretionRadius', nf.getValues('AccretionRadius') * self.units.conv['length'] )
        nf.setValues('FormationMass', nf.getValues('FormationMass') * self.units.conv['mass'] )
        if 'time' in self.cut:
            nf.setValues('FormationTime', nf.getValues('FormationTime') - self.cut['time'][0] )
        nf.setValues('FormationTime', nf.getValues('FormationTime') * self.units.conv['time'] )
        nf.setValues('AccretionRate', nf.getValues('AccretionRate') * self.units.conv['mass'] / self.units.conv['time'] )
        if 'accLum' in newKwargs:
            if 'time' in self.cut:
                nf.setValues('TimeOld', nf.getValues('TimeOld') - self.cut['time'][0] )
            nf.setValues('TimeOld', nf.getValues('TimeOld') * self.units.conv['time'] )
        #nf.getValues('HomeTask', np.zeros_like(nf.getValues('HomeTask')) )
        #nf.getValues('Index', np.zeros_like(nf.getValues('Index')) )

        # save the new sink file
        nf.write(fileName)
        nf.show(order='Mass',reverse=True,limit=10)

    def _cutCoords(self,data):
        if 'coord' in self.cut:
            ids = (self.cut['coord'][0]<data[:,0]) & (data[:,0]<self.cut['coord'][1]) & \
                  (self.cut['coord'][2]<data[:,1]) & (data[:,1]<self.cut['coord'][3]) & \
                  (self.cut['coord'][4]<data[:,2]) & (data[:,2]<self.cut['coord'][5])
        else:
            ids = data[:,0]==data[:,0]
        return ids

    def setupSnap(self,fileNew):
        fileOld = self.sim.fileSnap(self.snap)
        apy.shell.printc('Cutting the snapshot...','g')
        apy.shell.printc('Reading snapshot: %s'%fileOld)

        f = hp.File(fileOld,'r')
        g = hp.File(fileNew,'w')

        # secondary cut parametes
        self.cut['bulkVel'] = np.zeros(3)
 
        nPart = f['Header'].attrs['NumPart_Total']
        nPartCut = np.zeros_like(nPart)
        
        pb = apy.shell.pb(vmax=7, label="Cutting the box")
    
        for p in range(6):
            pb.increase()
            if nPart[p]==0: continue
            
            partType = 'PartType%d'%p
            g.create_group( partType )
            
            # select all particles from the cutted region
            prop = 'Coordinates'
            data = f[partType][prop][:]
            ids = self._cutCoords(data)
            nPartCut[p] = ids.sum()
        
            # cut coordinates and shift them to the zero
            prop = 'Coordinates'
            data = f[partType][prop][:]
            data = data[ids]
            if 'coord' in self.cut:
                data = data - self.cut['coord'][::2]
            data = data * self.units.conv['length']
            g[partType].create_dataset(prop, data=data)
            
            # cut velocities and substract the bulk velocity
            prop = 'Velocities'
            data = f[partType][prop][:]
            data = data[ids]
            if (p==0):  # calculating bulk velocity only from the gas particles
                self.cut['bulkVel'][:] = np.mean(data, axis=0)
            data = data - self.cut['bulkVel']
            data = data * self.units.conv['velocity']
            g[partType].create_dataset(prop, data=data)
        
            # cut masses
            prop = 'Masses'
            if prop in f[partType]:
                data = f[partType][prop][:]
                data = data[ids]
                data = data * self.units.conv['mass']
                g[partType].create_dataset(prop, data=data)
            
            # cut internal energies
            prop = 'InternalEnergy'
            if prop in f[partType]:
                data = f[partType][prop][:]
                data = data[ids]
                data = data * self.units.conv['energy']
                g[partType].create_dataset(prop, data=data)

            # cut other properties
            props = ['ChemicalAbundances','Gamma','ParticleIDs',
                     'MagneticField','MagneticFieldDivergence','PotentialPeak']
            for prop in props:
                if prop in f[partType]:
                    data = f[partType][prop][:]
                    data = data[ids]
                    g[partType].create_dataset(prop, data=data)

        # create header attributes
        g.create_group('Header')
        g['Header'].attrs.create('NumPart_ThisFile',nPartCut)
        g['Header'].attrs.create('NumPart_Total',nPartCut)
        boxsize = (self.cut['coord'][1]-self.cut['coord'][0]) if ('coord' in self.cut) else f['Header'].attrs['BoxSize']
        g['Header'].attrs.create('BoxSize',boxsize * self.units.conv['length'])
        time = (f['Header'].attrs['Time']-self.cut['time'][0]) if ('time' in self.cut) else f['Header'].attrs['Time']
        g['Header'].attrs.create('Time',time * self.units.conv['time'])
        g['Header'].attrs.create('UnitLength_in_cm',self.units.new['length'])
        g['Header'].attrs.create('UnitMass_in_g',self.units.new['mass'])
        g['Header'].attrs.create('UnitVelocity_in_cm_per_s',self.units.new['velocity'])
        props = ['NumPart_Total_HighWord','MassTable',
                 'Redshift','NumFilesPerSnapshot','Omega0','OmegaLambda','OmegaBaryon','HubbleParam',
                 'Flag_Sfr','Flag_Cooling','Flag_StellarAge','Flag_Metals','Flag_Feedback','Flag_DoublePrecision',
                 'Composition_vector_length']
        for prop in props:
            g['Header'].attrs.create(prop,f['Header'].attrs[prop])

        pb.increase()
        pb.close()
        
        # display value changes
        tab = apy.data.table()
        tab.column('Header parameter',['Time','BoxSize','UnitLength_in_cm','UnitMass_in_g','UnitVelocity_in_cm_per_s'])
        tab.column('Old value',[
            f['Header'].attrs['Time'],
            f['Header'].attrs['BoxSize'],
            f['Header'].attrs['UnitLength_in_cm'],
            f['Header'].attrs['UnitMass_in_g'],
            f['Header'].attrs['UnitVelocity_in_cm_per_s'],
        ])
        tab.column('New value',[
            g['Header'].attrs['Time'],
            g['Header'].attrs['BoxSize'],
            g['Header'].attrs['UnitLength_in_cm'],
            g['Header'].attrs['UnitMass_in_g'],
            g['Header'].attrs['UnitVelocity_in_cm_per_s'],
        ])
        tab.column('Old units',[
            self.units.guess('time',utype='old'), '', 
            self.units.guess('length',utype='old'), 
            self.units.guess('mass',utype='old'),
            self.units.guess('time',utype='old'),
        ])
        tab.column('New units',[
            self.units.guess('time',utype='new'), '', 
            self.units.guess('length',utype='new'), 
            self.units.guess('mass',utype='new'), 
            self.units.guess('time',utype='new'), 
        ])
        tab.show()

        print( 'NumPart old:', f['Header'].attrs['NumPart_Total'] )
        print( 'NumPart new:', g['Header'].attrs['NumPart_Total'] )

        f.close()
        g.close()

        apy.shell.printc('Writing snapshot:  %s'%fileNew)
