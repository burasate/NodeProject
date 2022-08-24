import json,os,pprint,sys,time,shutil
import datetime as dt

"""
Init
"""
rootPath = os.path.dirname(os.path.abspath(__file__))
srcPath = rootPath+'/src'
sitePackagePath = rootPath+'/src'+'/site-packages'

if not rootPath in sys.path:
    sys.path.insert(0,rootPath)
if not srcPath in sys.path:
    sys.path.insert(0,srcPath)
if not sitePackagePath in sys.path:
    sys.path.insert(0,sitePackagePath)
#Environment Linux
if not os.name == 'nt':
    sys.path.remove(sitePackagePath)

# Module
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
from gSheet import gSheet
gSheet.sheetName = 'Node Project Integration'
from notionDatabase import notionDatabase

# Path
prev_dir = os.sep.join(rootPath.split(os.sep)[:-1])
rec_dir = prev_dir + '/production_rec'
notiondb_dir = rec_dir + '/notionDatabase'

"""
Func
"""

def workspaceSetup(*_):
    path = os.sep.join(rootPath.split(os.sep)[:-1]) #\project name
    workspaceJ = json.load(open(rootPath + '/workspace.json', 'r'))
    for data in workspaceJ:
        name = data['name']
        makePath = path+'/{}'.format(name)
        if not os.path.isdir(makePath):
            os.makedirs(makePath)
            print('Create Dir {}'.format(makePath))

def versionBackup(extension, dirPath, dateFormat='%Y%m%d_%H%M%S'):
    if not '.' in extension:
        print('Skip backup version because [{}]'.format(extension))
        return None
    if not os.path.exists(dirPath):
        print('Skip backup version because path [{}]'.format(dirPath))
        return None
    for root, dirs, files in os.walk(dirPath, topdown=False):
        for name in files:
            filePath = os.path.join(root, name)
            if 'version' in filePath:
                continue
            if extension in filePath and not '.ini' in filePath:
                versionDir = root + '/version'
                mtime = os.stat(filePath).st_mtime
                dateStr = dt.datetime.fromtimestamp(mtime).strftime(dateFormat)
                new_fileName = name.replace(extension,'') + '_' + dateStr + extension
                new_filePath = root + os.sep + 'version' + os.sep + new_fileName
                if not os.path.exists(versionDir):
                    os.mkdir(versionDir)
                # print(maFilePath)
                if not os.path.exists(new_filePath) and not dateStr in name:
                    print('Backup {}'.format(new_filePath))
                    shutil.copyfile(filePath, new_filePath)

class integration:
    def load_notion_db(*_):
        if not os.path.exists(notiondb_dir):
            os.makedirs(notiondb_dir)
        notionDatabase.loadNotionDatabase(notiondb_dir)

    def notion_sheet(*_):
        base_path = os.sep.join(rootPath.split(os.sep)[:-1]).replace('\\','/')
        nt_csv_dir = base_path + '/production_rec/notionDatabase/csv'
        csv_path_list = [nt_csv_dir + '/' + i for i in os.listdir(nt_csv_dir)]
        #print(csv_path_list)
        for csv_path in csv_path_list:
            sheet_dest_name = 'nt_{}'.format(csv_path.split('/')[-1].split('.')[0])
            print('upload destination sheet', sheet_dest_name)
            try:
                gSheet.updateFromCSV(csv_path, sheet_dest_name)
            except:
                print('can\'t upload dataframe to sheet {}'.format(sheet_dest_name))





if __name__ == '__main__':
    base_path = os.sep.join(rootPath.split(os.sep)[:-1])
    #workspaceSetup()
    #versionBackup('.ma', base_path)
    #integration.load_notion_db()
    #integration.notion_sheet()

    pass