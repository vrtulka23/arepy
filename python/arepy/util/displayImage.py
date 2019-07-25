# Display an image using the 'display'
import subprocess

def displayImage( fileName='figOverview_*.png' ):    
    subprocess.call(["display", fileName ])
