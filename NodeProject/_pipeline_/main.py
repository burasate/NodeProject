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

#Internet Checking
while not has_internet():
    print(has_internet())
    now = str(dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    print('{}   no internet connection!'.format(now))
    time.sleep(10)

"""-----------------------"""
# Discord Bot
"""-----------------------"""
if not os.name == 'nt':
    os.system('cls||clear')
    raspi_update.update()
    dcbot_path = rootPath + '/raspi_dcbot.py'
    try:
        print('Open {}'.format(dcbot_path))
        subprocess.call(['lxterminal', '-e','python3.10 {}'.format(dcbot_path)])
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()))

while True:
    try:
        while not has_internet():
            os.system('cls||clear')
            print('{}   no internet connection!')
            time.sleep(30)

        print(os.system('cls||clear'))
        dateTime = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(dateTime)

        """
        System Manager (backup any important file in pipeline)
        """
        print('========\nSystem Manager\n========')
        importlib.reload(system_manager)
        # Fika Project
        if os.name == 'nt':
            system_manager.fika.cache_layout_file()
            # system_manager.versionBackup('.ma', r'C:\Fika\Projects\Dug\Shots', dateFormat='%Y%m%d_%H%M')
            # system_manager.versionBackup('.ma', r"D:\GDrive\Temp\Fika\Works", dateFormat='%Y%m%d_%H%M')
            # system_manager.versionBackup('.mov', r"D:\GDrive\Temp\Fika\Works", dateFormat='%Y%m%d_%H%M')
            system_manager.fika.ttf_ma_stat()
            system_manager.fika.stat_upload()
            # system_manager.fika.studio_library()

        importlib.reload(system_manager)
        system_manager.workspaceSetup()
        system_manager.integration.init_notion_db()
        system_manager.integration.load_notion_db()
        system_manager.data.create_history()
        system_manager.data.clear_past_history()
        #data cleanup
        system_manager.integration.notion_sheet()
        #system_manager.versionBackup('.ma', projectPath + '/animation_wrk', dateFormat='%Y%m%d_%H%M')
        #system_manager.versionBackup('.mov', projectPath + '/animation_xpt', dateFormat='%Y%m%d_%H%M')

        """
        Production Manager (update, record and cleanup data of production)
        """
        print('========\nProduction Manager\n========')
        importlib.reload(production_manager)
        #production_manager.loadNotionDatabase(projectPath + '/production_rec/notionDatabase')
        production_manager.register.update_member()
        production_manager.finance.auto_generate_document()
        production_manager.task_queue.run()

        # Quote Daily Task
        if os.name == 'nt':
            qd = production_manager.quote_daily()
            qd.load_podcast_transcript()
            for i in range(100):
                qd.add_new_quote()

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
        system_manager.error.record( str(traceback.format_exc()) )
    finally:
        print('Ending of Process')
        time.sleep(120)