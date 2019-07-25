import csv
import numpy as np
import arepy as apy

# This class creates a simple text file
# with the output times

class olist:
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        return

    def __init__(self,fileName=None):
        self.times = []
        if fileName is not None:
            self.read(fileName)
        
    def read(self,fileName):
        with open(fileName) as f:
            reader = csv.reader(f,delimiter='\t')
            for row in reader:
                self.setValue(row[0],row[1])

    def write(self,fileName):
        with open(fileName, 'wb') as f:
            writer = csv.writer(f,delimiter='\t')
            for time in self.times:
                writer.writerow(['%.07f'%time[0],time[1]])

    def show(self):
        tab = apy.data.table()
        tab.header(['Time','Status'])
        for time in self.times:
            tab.row(time)
        tab.show()

    def setValue(self,time,status=1):
        if np.isscalar(time):
            self.times.append( (time,status) )
        else:
            for t in time:
                self.times.append( (t,status) )
