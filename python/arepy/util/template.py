import arepy as apy

class template:
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        return

    def __init__(self,fileName,mark="{{%s}}"):
        self.mark = mark
        self.fileName = fileName
        self.changes = {}
        with open(fileName,'r') as f:
            self.template = str(f.read())

    def replace(self,name,value=None):
        if isinstance(name,dict):
            for name,value in name.items():
                self.changes[name] = value
        else:
            self.changes[name] = value
            
        
    def write(self,fileName=None):
        for name,value in self.changes.items():
            self.template = self.template.replace( self.mark%name, str(value) )
        fileName = self.fileName if fileName==None else fileName
        dirName = apy.shell.dirname(fileName)
        if not apy.shell.isdir(dirName):
            apy.shell.prompt("Directory \"%s\"\ndoes not exist. Do you want to create it?"%dirName)
            apy.shell.mkdir(dirName)
        with open(fileName,'w') as f:
            f.write(self.template)
