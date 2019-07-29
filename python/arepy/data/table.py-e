import arepy as apy
import numpy as np
import matplotlib as mpl
import os

class table:
    def __init__(self,**opt):
        self.columns = []
        self.headers = []
        self.rows = []
        self.notes = []

        # set options
        self.opt = {
            'debug':False,
            'dirResults':'results',
            'dirName':None,
            'fileName':'figOverview', 
            'timeStamp': apy.util.timeStamp(),
            'fileFormat': 'tabulate',
        }
        self.opt.update(opt)

        if self.opt['debug']:
            apy.shell.printc('Debugging mode is on!!!','r')
            self.opt['timeStamp'] = 'debug'

        self.dirName = self.opt['fileName'] if self.opt['dirName'] is None else self.opt['dirName']
        self.dirResults = self.opt['dirResults']+'/'+self.dirName+'/'+self.opt['timeStamp'] 
        extension = {'tabulate':'.txt','csv':'.csv'}
        self.fileName = self.dirResults+'/'+self.opt['fileName']+extension[self.opt['fileFormat']]

    def column(self,header,data):
        self.columns.append( data )
        self.headers.append( header )

    def header(self,data):
        self.headers = data

    def row(self,data):
        self.rows.append( data )

    def _note(self,name,value):
        self.notes.append({'name':name,'value':value})
    def note(self,value1,value2=None):
        if isinstance(value1,dict):
            for name,value in value1.items():
                self._note(name,value)
        else:
            self._note(value1,value2)            

    def show(self,limit=None):
        data = np.array(self.columns).T if len(self.columns)>0 else self.rows
        ndata = len(data)
        if limit is not None and limit<ndata:
            data = data[:limit]
        for note in self.notes:
            print( "%-20s"%note['name'], note['value'] )
        print( apy.data.tabulate( data, headers=self.headers ) )
        if limit is not None and limit<ndata:
            print( 'Showing %d out of %d rows'%(limit, ndata) )

    def save(self):
        apy.shell.mkdir(self.dirResults,'u')
        data = np.array(self.columns).T if len(self.columns)>0 else self.rows
        if self.opt['fileFormat']=='tabulate':
            text = apy.data.tabulate( data, headers=self.headers )        
            with open(self.fileName, "w") as f:
                for note in self.notes:
                    f.write('%-20s %s \n'%(note['name'],note['value']))
                f.write(text)
                f.close()
        elif self.opt['fileFormat']=='csv':
            import csv
            with open(self.fileName, mode='w') as f:
                writer = csv.writer(f, delimiter=' ')
                writer.writerow(self.headers)
                for dat in data:
                    writer.writerow(dat)
        apy.shell.printc('Table saved as: %s'%(self.fileName))

    def plot(self,xheader,yheaders,xlabel=None,ylabel=None,xlog=False,ylog=False,marker='|',
             hline=None,xlim=None,ylim=None,grid=False,show=False,savefig=False,display=False):
        if isinstance(yheaders,str):
            yheaders = [yheaders]
        if xlabel==None:
            xlabel = xheader
        if ylabel==None:
            ylabel = yheaders[0]

        fig = mpl.pyplot.figure(figsize=(4,3))
        ax = mpl.pyplot.subplot(111)
        
        for yheader in yheaders:
            x = self.headers.index(xheader)
            y = self.headers.index(yheader)
            data = self.columns if len(self.columns)>0 else np.array(self.rows).T
            ax.plot(data[x],data[y],label=yheader,marker=marker)

        if hline: ax.axhline(hline,color='grey')
        if xlog: ax.set_xscale('log')
        if ylog: ax.set_yscale('log')
        if len(yheaders)>1: ax.legend()
        if xlim: ax.set_xlim(xlim)
        if ylim: ax.set_ylim(ylim)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if grid: mpl.pyplot.grid(True)

        mpl.pyplot.tight_layout()
        if show: mpl.pyplot.show()
        if savefig: 
            mpl.pyplot.savefig(savefig)
            if display:
                apy.util.displayImage(savefig)
