import arepy as apy
import numpy as np

class correlate:
    def __init__(self,xdata,ydata=None):
        """Correlation matrix class

        :param list xdata: List of x-data
        :param list ydata: List of y-data
        """
        self.xdata = xdata
        self.ydata = list(reversed(xdata)) if ydata is None else ydata
        self.ncol = len(self.xdata)
        self.nrow =  len(self.ydata)
    
    def getMatrix(self,edge=1):
        """Create a correlation map from the data
    
        :param int edge: Starting edge of the correlation matrix 
        :return: list of touples in a form (row,column,xdata,ydata)

        edges:
        0) return whole matrix
        1) left top (default)
        2) right bottom 
        """
        data = []
        for col in range(self.ncol):
            for row in range(self.nrow):
                if edge==1 and col>=(self.ncol-row-1): continue
                elif edge==2 and col<=(self.ncol-row-1): continue
                else: data.append((row,col,self.xdata[col],self.ydata[row]))
        return data

    def getHistograms(self,bins=100,xy=1):
        """Create histograms from the data

        :param int bins: Number of bins
        :param int xy: Choice of the histogram data sets
        :return: Histograms
        
        xy:
        0) histograms of both x and y data
        1) histograms of x data only (default)
        2) histograms of y data only
        3) 2D histograms of x/y data
        """
        data = []
        if xy in [0,1]:   
            for xdata in self.xdata:
                print(xdata)
                data.append( np.histogram(xdata,bins=bins) )
        elif xy in [0,2]:
            for ydata in self.ydata:
                data.append( np.histogram(ydata,bins=bins) )
        elif xy==3:
            for xdata in self.xdata:
                for ydata in self.ydata:
                    data.append( np.histogram2d(xdata,ydata,bins=bins) )
        return data

'''
def correlate(xdata,ydata=None,edge=0):
    """Create a correlation map from the data
    
    :param list xdata: List of x-data
    :param list ydata: List of y-data
    :param int edge: Starting edge of the correlation matrix 

    Edges:
    0) left top 
    1) right bottom 
    2) left bottom 
    3) right top 
    """
    if ydata is None:
        ydata = list(reversed(xdata))
    ncols,nrow = len(xdata), len(ydata)
    data = []
    for col in range(ncols):
        for row in range(nrow):
            if edge==0 and col<(ncols-row-1):
                data.append((row,col,xdata[col],ydata[row]))
            elif edge==1 and col>(ncols-row-1):  
                data.append((row,col,xdata[col],ydata[row]))
            else:
                continue
    return data # (row,column,xdata,ydata)
'''
