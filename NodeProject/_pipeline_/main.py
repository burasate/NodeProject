import json,os,pprint,sys,time,shutil,importlib
import datetime as dt
import subprocess

"""
Init
"""
time.sleep(15)
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
    os.system('cls||clear')
    print(p)

"""
Cycle System
"""
#time.sleep(15)
import production_manager
import system_manager
import raspi_update

# Discord Bot
if not os.name == 'nt':
    os.system('cls||clear')
    dcbot_path = rootPath + '/raspi_dcbot.py'
    print('Open {}'.format(dcbot_path))
    try:
        raspi_update.update()
        subprocess.call(['lxterminal', '-e','python3 {}'.format(dcbot_path)])
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()))

while True:
    try:
        if not os.name == 'nt':
            importlib.reload(raspi_update)
            raspi_update.update()
            time.sleep(3)

        print(os.system('cls||clear'))
        dateTime = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(dateTime)

        """
        System Manager (backup any important file in pipeline)
        """
        print('========\nSystem Manager\n========')
        importlib.reload(system_manager)
        system_manager.workspaceSetup()
        #system_manager.versionBackup('.ma', projectPath + '/animation_wrk', dateFormat='%Y%m%d_%H%M')
        #system_manager.versionBackup('.mov', projectPath + '/animation_xpt', dateFormat='%Y%m%d_%H%M')

        """
        Production Manager (update, record and cleanup data of production)
        """
        print('========\nProduction Manager\n========')
        importlib.reload(production_manager)
        production_manager.loadNotionDatabase(projectPath + '/production_rec/notionDatabase')
        production_manager.register.updateMember()
        production_manager.taskQueue.run()

        """
        Data Analytic (data analysis and report)
        """
        print('========\nData Analytic\n========')
        importlib.reload(system_manager)

    except Exception as e:
        import traceback
        print('!!!! ==========================')
        print(str(traceback.format_exc()))
        print('!!!! ==========================')
    finally:
        print('Ending of Process')
        time.sleep(600*0.1)