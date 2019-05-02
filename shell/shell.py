from subprocess import call
import arepy as apy
import os, sys

def textc(text,color='y'):
    colors = {'red': "\033[1;31m",    'r': "\033[1;31m",  
              'blue': "\033[1;34m",   'b': "\033[1;34m",
              'cyan': "\033[1;36m",   'c': "\033[1;36m",
              'orange': "\033[1;91m", 'o': "\033[1;91m",
              'green': "\033[0;32m",  'g': "\033[0;32m",
              'yellow': "\033[0;33m", 'y': "\033[0;33m",
              'reset': "\033[0;0m",
              'bold': "\033[;1m",
              'reverse': "\033[;7m"}
    return colors[color] + text + colors['reset']

def printc(text,color='y'):
    print( textc(text,color) )

def prints(name,data,show=None):
    print( apy.data.stats(name,data,show) )

def exit(msg=None):
    if msg:
        printc('\nError: %s'%str(msg),'r')
        sys.exit()
    else:
        sys.exit()

def isfile(fileName):
    return os.path.isfile(fileName)

def isdir(dirName):
    return os.path.isdir(dirName)

def option(msg,opt):
    msgStr = str(msg)
    optStr = [str(o) for o in opt]
    optStr[0] = optStr[0].upper()
    optStr = "/".join(optStr)
    question = textc('\n%s (%s) '%(msgStr,optStr),'b')    
    answer = input(question)
    return answer

def prompt(msg):
    question = textc('\n%s (Y/n) '%str(msg),'b')
    answer = input(question)
    if answer in ['n','N']:
        sys.exit()

def cp(fileFrom,fileTo):
    if isdir(fileFrom):
        prompt('You are copying a directory. Continue?')
    call(['cp','-r',fileFrom,fileTo])

def rm(path):
    call(['rm','-r',path])
    
def mkdir(dirName,opt=None):
    if isdir(dirName):
        if opt is None:
            opt = option('Directory \"%s\"\nalready exists. Do you want use/overwrite it or exit?'%dirName,['u','o','e'])
        if opt=='e':
            sys.exit()
        elif opt=='o':
            rm( dirName )
        else:
            return
    call(['mkdir','-p',dirName])

def link(srcName,linkName):
    call(['ln','-s',srcName,linkName])
    
def touch(fileName):
    call(['touch',fileName])

def dirname(fileName):
    return os.path.dirname(fileName)
        
