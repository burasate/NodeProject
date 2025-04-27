import json, os, pprint, sys, time, shutil, importlib, subprocess, getpass
import datetime as dt
import random

"""
Init
"""

os.system('cls||clear')
print('========\nInitialize\n========')

base_path = os.path.dirname(os.path.abspath(__file__))
src_path = base_path+'/src'
site_package_path = base_path+'/src'+'/site-packages'
project_path = os.sep.join(base_path.split(os.sep)[:-1])

#Environment
if not os.name == 'nt': #Linux
	pass
else:
	if not base_path in sys.path:
		sys.path.insert(0, base_path)
	if not src_path in sys.path:
		sys.path.insert(0, src_path)
	if not site_package_path in sys.path:
		sys.path.insert(0, site_package_path)

for p in sys.path:
    print(p)

def get_ssid_name():
	os_name = os.name
	if os_name == 'nt': # windows
		ssid_encode = subprocess.check_output("netsh wlan show interfaces")
		ssid_decode = ssid_encode.decode().strip()
		print(ssid_decode)
		ssid_find = [i.strip() for i in ssid_decode.split('\n')]
		ssid_find = [i for i in ssid_find if i.startswith('SSID')]
		if ssid_find:
			ssid = ssid_find[0].split(':')[-1].strip()
			return ssid
		else:
			raise Warning('can\'t found ssid or wlan is disconnected')
	elif os_name == 'posix': # raspberry pi
		ssid_encode = subprocess.check_output("iwgetid")
		ssid_decode = ssid_encode.decode().strip()
		print(ssid_decode)
		ssid_find = [i.strip() for i in ssid_decode.split('\n')]
		ssid_find = [i for i in ssid_find if 'SSID' in i]
		if ssid_find:
			ssid = ssid_find[0].split(':')[-1].strip().replace('\"', '')
			return ssid
		else:
			raise Warning('can\'t found ssid or wlan is disconnected')

"""-----------------------"""
#Update System
"""-----------------------"""
if not os.name == 'nt': #Linux
	import raspi_update

"""-----------------------"""
#Cycle System
"""-----------------------"""
import production_manager
import system_manager

#Internet Connection
import requests
def has_internet():
    try:
        r = requests.get('https://google.com')
    except:
        return False
    else:
        return True

#Internet Checking
while not has_internet():
    print(has_internet())
    now = str(dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    print('{}   no internet connection!'.format(now))
    time.sleep(10)

"""-----------------------"""
# Init Config
"""-----------------------"""
appdata_path = os.getenv('APPDATA') if os.name == 'nt' else os.path.expanduser('~/.config')
node_project_dir = os.path.join(appdata_path, 'node_project')
if not os.path.exists(node_project_dir):
    os.makedirs(node_project_dir)
'''
config_path = os.path.join(node_project_dir, 'config.json')
if os.path.exists(config_path):
    with open(config_path) as f:
        content = f.read().strip()
        if content:
            config = json.loads(content)
            config['info']['ssid'] = get_ssid_name()
else:
	config = {
		'info' : {
			'user': getpass.getuser(),
			'ssid': get_ssid_name(),
		}
	}
json.dump(config, open(config_path, 'w'), indent=4)
'''

"""-----------------------"""
# Discord Bot
"""-----------------------"""
if not os.name == 'nt': # posix
    os.system('cls||clear')
    raspi_update.update()
    dcbot_path = base_path + '/raspi_dcbot.py'
    try:
        print('Open {}'.format(os.path.basename(dcbot_path)))
        time.sleep(1.5)
        subprocess.call( ['lxterminal', '-t', 'Discord Node', '-e','python3 {}'.format(dcbot_path)] ) #python 3.7
        #subprocess.call( ['lxterminal', '-t', 'Discord Node', '-e','python3.10 {}'.format(dcbot_path)] ) #python 3.10
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()))
        time.sleep(10)

"""-----------------------"""
# Edge Systems Opening
"""-----------------------"""
while True:
    try:
        print(os.system('cls||clear'))
        dateTime = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(dateTime)
        while not has_internet():
            os.system('cls||clear')
            print(' - no internet connection!')
            time.sleep(30)

        """
        System Manager (backup any important file in pipeline)
        """
        print('========\nSystem Manager\n========')
        importlib.reload(system_manager)
        system_manager.workspaceSetup()
        system_manager.integration.init_notion_db()
        system_manager.integration.load_notion_db()
        system_manager.data.create_history()
        system_manager.data.clear_past_history()
        #data cleanup
        system_manager.integration.notion_sheet()
        #system_manager.versionBackup('.ma', project_path + '/animation_wrk', dateFormat='%Y%m%d_%H%M')
        #system_manager.versionBackup('.mov', project_path + '/animation_xpt', dateFormat='%Y%m%d_%H%M')

        """
        Production Manager (update, record and cleanup data of production)
        """
        print('========\nProduction Manager\n========')
        importlib.reload(production_manager)
        #production_manager.loadNotionDatabase(project_path + '/production_rec/notionDatabase')
        production_manager.register.update_member()
        production_manager.finance.auto_generate_document()
        tq = production_manager.task_queue()
        tq.run()

        '''
        # Quote Daily Task
        if os.name == 'nt' and random.randint(0, 5) == 5:
            qd = production_manager.quote_daily()
            qd.load_podcast_transcript()
            for i in range(50):
                qd.add_new_quote()
        '''

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