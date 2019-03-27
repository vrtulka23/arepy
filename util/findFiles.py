# Find all files that match a certain pattern
#
# example:
# snaps = findFiles( 'output', 'snap_([0-9]+).hdf5', dtParam=int )
#
def findFiles( fileDir, pattern, dtParam=False ):
    import glob, re, os
    if dtParam:
        params = []
        for f in os.listdir(fileDir):
            m = re.search(pattern,f)
            if m:
                params.append( m.group(1) )
        params.sort(key=dtParam)
        return map(dtParam,params)
    else:
        os.chdir(fileDir)
        return glob.glob(pattern)
