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


if __name__ == '__main__':
    mainPath = os.sep.join(rootPath.split(os.sep)[:-1])
    #workspaceSetup()
    #versionBackup('.ma', mainPath)
    pass