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
    print(proj)
    exec("from %s import *"%(proj))
    p = project(proj)
    if fn=='setup':
        p.setup(*args)
    elif fn in ['plot','debug','show','movie']:
        p.plot(fn,*args)
    elif fn=='script':
        p.script(*args)
    elif fn=='init-setup':
        p.initSetup(*args)
    elif fn=='init-plot':
        p.initPlot(*args)
    elif fn=='init-script':
        p.initScript(*args)
elif fn=='init-proj':    
    from arepy.scripy.project import *
    p = project(proj)
    p.initProj(*args)    
else:
    exec("from %s.%s import main"%(proj,fn))
    main(*args)
