import json,os,pprint,sys,time,shutil,importlib
import datetime as dt
import subprocess

"""
Init
"""
if not os.name == 'nt':
    time.sleep(5)

os.system('cls||clear')
print('========\nInitialize\n========')

rootPath = os.path.dirname(os.path.abspath(__file__))
srcPath = rootPath+'/src'
sitePackagePath = rootPath+'/src'+'/site-packages'
projectPath = os.sep.join(rootPath.split(os.sep)[:-1])

#Environment
if not rootPath in sys.path:
    sys.path.insert(0,rootPath)
if not srcPath in sys.path:
    sys.path.insert(0,srcPath)
if not sitePackagePath in sys.path:
    sys.path.insert(0,sitePackagePath)
#Environment Linux
if not os.name == 'nt':
    sys.path.remove(sitePackagePath)

for p in sys.path:
    print(p)

"""
Update
"""
import raspi_update
raspi_update.update()
