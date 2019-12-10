# Display an image using the 'display'
import subprocess
import arepy as apy
import os

def displayImage( fileName='figOverview_*.png' ):    
    from sys import platform
    if platform == "linux" or platform == "linux2":
        if apy.config["imageViewer"] == "gpicview":
            folder, fname = os.path.split(fileName)
            subprocess.call([apy.config["imageViewer"], *apy.util.findFiles(folder, fname)])
        else:
            subprocess.call([apy.config["imageViewer"], fileName ])
    elif platform == "darwin":
        print(fileName)
        subprocess.call(["open", fileName ])
    elif platform == "win32":
        subprocess.call(["display", fileName ])
    
