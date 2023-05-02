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

#Internet Connection
import requests
def has_internet():
    try:
        r = requests.get('https://google.com')
    except:
        return False
    else:
        return True

"""
Cycle System
"""
import production_manager
import system_manager
import raspi_update


while True:
    try:
        # Quote Daily Task
        qd = production_manager.quote_daily()
        #qd.load_podcast_transcript()
        while True:
            for i in range(7):
                qd.add_new_quote()
            time.sleep(20)

    except Exception as e:
        import traceback
        print('!!!! ==========================')
        print(str(traceback.format_exc()))
        print('!!!! ==========================')
        system_manager.error.record( str(traceback.format_exc()) )
    finally:
        print('Ending of Process')
        time.sleep(20)