import numpy as np
import arepy as apy
import h5py as hp

class subfind:
    def __init__(self,fileName=None):
        if fileName is not None:
            self.read(fileName)

    def read(self,fileName):
        self.fileName = fileName
        self.pt = [(t,'PartType%d'%t) for t in [0]]
        with hp.File(self.fileName%(0),'r') as f:
            self.units = {key: f['Units'].attrs[key] for key in f['Units'].attrs.keys()}
            self.units['h'] = f['Header'].attrs['HubbleParam']
            self.units['a'] = f['Header'].attrs['ExpansionFactor']
            self.units['z'] = f['Header'].attrs['Redshift']            
            self.nfiles = f['FOF'].attrs['NTask']
            
        self.sub = apy.data.collector()
        self.fof = apy.data.collector()
        self.part = [apy.data.collector() for t,pt in self.pt]
        for fid in range(0,self.nfiles):
            with hp.File(self.fileName%fid,'r') as f:
                nfofTot = f['SUBFIND'].attrs['Total_Number_of_groups']
                nsubTot = f['SUBFIND'].attrs['Total_Number_of_subgroups']
                npartTot = f['FOF'].attrs['Total_Number_per_Type']   
                nfof = f['SUBFIND'].attrs['Number_of_groups']
                nsub = f['SUBFIND'].attrs['Number_of_subgroups']
                npart = f['FOF'].attrs['Number_per_Type']
                self.fof.add(fid,nfofTot,nfof,{
                    'Halo_M_Mean200':       f['SUBFIND/Halo_M_Mean200'],
                    'Halo_M_TopHat200':     f['SUBFIND/Halo_M_TopHat200'],
                    'Halo_R_Mean200':       f['SUBFIND/Halo_R_Mean200'],
                    'FirstSubOfHalo':       f['SUBFIND/FirstSubOfHalo'],
                    'NsubPerHalo':          f['SUBFIND/NsubPerHalo'],
                })
                self.sub.add(fid,nsubTot,nsub,{
                    'CenterOfMass':         f['SUBFIND/CenterOfMass'][:].reshape((nsub,3)),
                    'Position':             f['SUBFIND/Position'][:].reshape((nsub,3)),
                    'Mass':                 f['SUBFIND/Mass'],
                    'MassType':             f['SUBFIND/MassType'][:].reshape((nsub,6)),
                    'PartType0/SUB_Length': f['FOF/PartType0/SUB_Length'],
                    'PartType0/SUB_Offset': f['FOF/PartType0/SUB_Offset'],
                })
                for t,pt in self.pt:
                    self.part[t].add(fid,npartTot[t],npart[t],{
                        pt+'/ParticleIDs': f['FOF/'+pt+'/ParticleIDs'],
                        pt+'/Mass':        f['FOF/'+pt+'/Mass'],
                        pt+'/Coordinates': f['FOF/'+pt+'/Coordinates'][:].reshape((npart[t],3))
                    })

        # select only halos found by subfind
        self.halos = {}
        idfof = self.fof['NsubPerHalo']!=0
        for key in self.fof.keys():
            self.halos[key] = self.fof[key][idfof]

        # select only the first, main sub-halo
        idsub = self.halos['FirstSubOfHalo']
        for key in self.sub.keys():
            self.halos[key] = self.sub[key][idsub]        

        # select only halos that contain gas particles
        idhalo = self.halos['PartType0/SUB_Length']!=0
        for key in self.halos.keys():
            self.halos[key] = self.halos[key][idhalo]

        self.nHalos = idhalo.sum()

        # assign particles
        for t,pt in self.pt:
            self.halos[pt+'/ParticleIDs'] = []
            self.halos[pt+'/Mass'] = []
            self.halos[pt+'/Coordinates'] = []
            for h in range(self.nHalos):
                l = self.halos[pt+'/SUB_Length'][h]
                o = self.halos[pt+'/SUB_Offset'][h]
                pids = self.part[t][pt+'/ParticleIDs'][o:o+l]
                mass = self.part[t][pt+'/Mass'][o:o+l]
                coord = self.part[t][pt+'/Coordinates'][o:o+l]
                self.halos[pt+'/ParticleIDs'].append(pids)
                self.halos[pt+'/Mass'].append(mass)
                self.halos[pt+'/Coordinates'].append(coord)
