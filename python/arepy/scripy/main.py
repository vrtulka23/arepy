print("Loading scripy")
import arepy as apy
import sys,os
proj = sys.argv[1]
fn = sys.argv[2]
args = sys.argv[3:]

sys.path.insert(0, apy.dirScripy)

fns = ['setup','plot','debug','show','movie','script','init-setup','init-plot','init-script']
if fn in fns:
    if proj=='tmp':
        apy.shell.exit('Script "run.sh" was not found in this directory (main.py)')
    exec("from %s import *"%(proj))
    proj = project(proj)
    if fn=='setup':
        proj.setup(*args)
    elif fn in ['plot','debug','show','movie']:
        proj.plot(fn,*args)
    elif fn=='script':
        proj.script(*args)
    elif fn=='init-setup':
        proj.initSetup(*args)
    elif fn=='init-plot':
        proj.initPlot(*args)
    elif fn=='init-script':
        proj.initScript(*args)
elif fn=='init-proj':    
    from arepy.scripy.project import *
    proj = project(proj)
    proj.initProj(proj,*args)    
else:
    exec("from %s.%s import main"%(proj,fn))
    main(*args)
