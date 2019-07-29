import arepy as apy
import subprocess as sp

def makeMovie(fileName='movie.mp4', imgFiles='figOverview_*.png'):

    # ffmpeg -r 10 -pattern_type glob -i 'figOverview_*.png' -c:v libx264 -r 25 -pix_fmt yuv420p 'figOverview.mp4'

    '''
    command = [ 'ffmpeg',
                '-r', '10',                                # frames per second
                '-pattern_type', 'glob',                   # search pattern type
                '-i', '"%s"'%imgFiles,                     # input file (as string!!)
                '-c:v', 'libx264',                         # codec type
                '-r', '25',                                # frames per second
                '-pix_fmt', 'yuv420p',
                '-vf', "'pad=ceil(iw/2)*2:ceil(ih/2)*2'",  # ensure that w/h size is even
                '"%s"'%fileName ]                          # output file (as string!!)
    '''
    command = [
        'ffmpeg', 
        '-r', '10', 
        '-pattern_type', 'glob', 
        '-i', imgFiles, 
        #'-c:v', 'libx264',
        '-r', '25', 
        #'-pix_fmt', 'yuv420p', 
        #'-vf', "'pad=ceil(iw/2)*2:ceil(ih/2)*2'", 
        fileName
    ]
    apy.shell.printc( " ".join(command) )
    sp.call(command)
    #pipe = sp.Popen( command, stdin=sp.PIPE, stderr=sp.PIPE)

    
