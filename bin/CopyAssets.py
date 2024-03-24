#####################################################################################################################################################
# Copyright (c) 2006 Activision, Inc
#   Confidential Information of Activision.
#   Not for disclosure or distribution without Activision's prior written consent.
#####################################################################################################################################################


import os
import sys
import shutil
import stat
import time
import re
import logging
 
g_base_install_dir  = ""   #PC install Dir
g_base_game_dir     = ""             #P4 COD Root, env var? cmdline?

copy_directories = []

#################################################################################################################################################
# Flush the standard output and error streams
def flushStdStreams():
    if 'flush' in dir(sys.stdout):
        sys.stdout.flush()              # Serialize stdout and stderr
    if 'flush' in dir(sys.stderr):
        sys.stderr.flush()

def syncFile( srcFilename, destFilename ):
    if not os.path.exists(srcFilename):
        logging.warning("Src file does not exist!: " + (srcFilename) )
        return False
        
    if not os.path.exists(destFilename):
        if not os.path.exists( os.path.dirname(destFilename) ):
            os.makedirs(os.path.dirname(destFilename) )
            
        shutil.copyfile( srcFilename, destFilename )
        shutil.copystat( srcFilename, destFilename )
        os.chmod(destFilename,stat.S_IREAD|stat.S_IWRITE)
        logging.info('Getting: %s' %destFilename)
        return True
    else:
        srcStats = os.stat(srcFilename)
        dstStats = os.stat(destFilename)
        srcTime = time.localtime(srcStats[stat.ST_MTIME]) 
        dstTime = time.localtime(dstStats[stat.ST_MTIME])
        if ( srcTime != dstTime ):

            try:
                shutil.copyfile( srcFilename, destFilename )
                shutil.copystat( srcFilename, destFilename )
                os.chmod(destFilename,stat.S_IREAD|stat.S_IWRITE)
                logging.info( "Updating: %s" %destFilename )
                return True
            except:
                if os.path.exists(srcFilename):
                    logging.warning( "Cannot Copy File '%s'!" %(srcFilename) )
                else:
                    logging.warning( "File '%s' does not exist!" %(srcFilename) )
                return False
        else:
            logging.debug( "Up to date: " + destFilename )
            
    return False


#################################################################################################################################################
# Recursively copy an entire directory tree 
# @param src        src folder
# @param dst        dst path
# @param recursive  recursive copy or not (True by default)
# @param maskedStrings list of strings used to mask files (ie: files containing any of the maskedStrings won't be copied)
# @param filterFunctor optional function object for filtering out source files
def copytree(src, dst, recursive=True, regMatchExpression=None):
    totalFilesCopied = 0
    if os.path.isdir(src):
        
        numFiles = 0
        fileList = os.listdir(src)
        
        if not os.path.isdir(dst):
            os.makedirs(dst)
            
        for name in fileList:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)

            try:
                if os.path.isdir(srcname):
                    if recursive:
                        totalFilesCopied += copytree(srcname, dstname, recursive, regMatchExpression)
                else:
                    doCopy = True
                    
                    if regMatchExpression != None:
                        doCopy = False
                        m = regMatchExpression.match(srcname)
                        if m:
                            doCopy = True
                                                  
                    if doCopy:
                        if syncFile(srcname,dstname) :
                            totalFilesCopied+=1
                            
                        numFiles+=1
                        
                    if numFiles>100:
                        numFiles = 0
                        print ".",
                        flushStdStreams()
            except (IOError, os.error), why:
                logging.error(  "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why)) )
     
    return totalFilesCopied

def Usage():
    print 'Usage: CopyAssets.py [srcDir destDir config]'
    print 'Default: srcDir=IW_PROJECT_GAMEDIR, destDir=Current WOrking Directory, config=CopyAssets.config\n\n'
    
if __name__ == "__main__":
    
    configFile = ""

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename='copyAssets.log',
                        filemode='w')

    arg = sys.argv[1:]
    if len(arg) == 0:
        g_base_install_dir = os.getcwd()
        if g_base_install_dir.endswith('bin'):
            g_base_install_dir = os.path.abspath(os.path.join( g_base_install_dir, '../'))
          
        if 'cod5modtools' in g_base_install_dir:
            logging.error( 'Must run from PC Release directory, not the DEPOT!' )
            print 'Must run from PC Release directory, not the DEPOT!'
            sys.exit(1)
            
        g_base_game_dir = os.getenv('IW_PROJECT_GAMEDIR')
        if g_base_game_dir == "":
            logging.error( 'Must define IW_PROJECT_GAMEDIR env var or specify directory' )
            print 'Must define IW_PROJECT_GAMEDIR env var or specify directory'
            Usage()
            sys.exit(1)
        
        configFile = 'CopyAssets.config'
        if not os.path.isfile(configFile):
            logging.error( 'Could not find config file!' )
            print 'Could not find config file!'
            Usage()
            sys.exit(1)
        else:
            FILE = open(configFile,'r')
            exec(FILE)
            
    elif len(arg) == 3:
        g_base_game_dir     = os.path.expandvars(arg[0])
        if not os.path.isdir(g_base_game_dir):
            logging.error( 'Could not find source directory! ' + g_base_game_dir )
            print 'Could not find source directory! ' + g_base_game_dir 
            Usage()
            sys.exit(1)
            
        g_base_install_dir  = os.path.expandvars(arg[1])
        
        configFile = os.path.expandvars(arg[2])
        if not os.path.isfile(configFile):
            logging.error( 'Could not find config file!' )
            print 'Could not find config file!'
            Usage()
            sys.exit(1)
        else:
            FILE = open(configFile,'r')
            exec(FILE)   
    else:
        Usage()
        sys.exit(1)
    
    
    logging.info( 'Src Dir: ' + g_base_game_dir )
    logging.info( 'Dst Dir: ' + g_base_install_dir )
    logging.info( 'Config : ' + configFile )
    totalFileCopied = 0
    logging.info( 'Copying files...' )
    print  'Copying files...'
    for item in copy_directories:
        baseName = os.path.basename(item[0])
        srcPath = os.path.join( g_base_game_dir, item[0] )
        dstPath = os.path.join( g_base_install_dir, item[1] )
        recursiveCopy = True
        
        if len(item) >= 3:
            recursiveCopy = item[2]
            
        if len(item) == 4:
            reExp = re.compile(item[3]) 
            totalFileCopied += copytree(srcPath,dstPath,recursiveCopy,regMatchExpression=reExp)
        else:
           
            if os.path.isfile(srcPath):
                logging.info( 'Copying File' + srcPath + ' -> ' + dstPath )
                if syncFile(srcPath,dstPath):
                    totalFileCopied += 1
            elif os.path.isdir(srcPath):
                logging.info( 'Copying Dir' + srcPath + ' ----> ' + dstPath )
                totalFileCopied += copytree(srcPath,dstPath,recursiveCopy)
    
    logging.info( 'Copied ' + str(totalFileCopied) + ' files!' )

            