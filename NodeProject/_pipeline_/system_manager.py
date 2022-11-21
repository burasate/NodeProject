# -*- coding: utf-8 -*-
import json,os,pprint,sys,time,shutil
import datetime as dt

"""
Init
"""
root_path = os.path.dirname(os.path.abspath(__file__))
src_path = root_path+'/src'
site_package_path = root_path+'/src'+'/site-packages'

if not root_path in sys.path:
    sys.path.insert(0,root_path)
if not src_path in sys.path:
    sys.path.insert(0,src_path)
if not site_package_path in sys.path:
    sys.path.insert(0,site_package_path)
#Environment Linux
if not os.name == 'nt':
    sys.path.remove(site_package_path)

# Module
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
from gSheet import gSheet
gSheet.sheetName = 'Node Project Integration'
from notionDatabase import notionDatabase as ntdb
from maReader import maReader

# Path
prev_dir = os.sep.join(root_path.split(os.sep)[:-1])
rec_dir = prev_dir + '/production_rec'
notiondb_dir = rec_dir + '/notionDatabase'

"""
Func
"""

def workspaceSetup(*_):
    path = os.sep.join(root_path.split(os.sep)[:-1]) #\project name
    workspaceJ = json.load(open(root_path + '/workspace.json', 'r'))
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

def load_worksheet(sheet, dir_path):
    data = gSheet.getAllDataS(sheet)
    save_path = dir_path + os.sep + sheet + '.json'
    json.dump(data, open(save_path, 'w'), indent=4)
    print('Load worksheet {} - {}'.format(gSheet.sheetName,sheet))

class integration:
    def init_notion_db(*_):
        load_worksheet('nt_database', rec_dir)
        db_path = rec_dir + '/nt_database.json'
        with open(db_path) as db_f:
            db_j = json.load(db_f)

        with open(ntdb.config_path) as r_config_f:
            r_config_j = json.load(r_config_f)
            r_config_j['database'] = db_j
        with open(ntdb.config_path, 'w') as w_config_f:
            json.dump(r_config_j, w_config_f,indent=4)

        ntdb.database = r_config_j['database']

    def load_notion_db(*_):
        if not os.path.exists(notiondb_dir):
            os.makedirs(notiondb_dir)
        ntdb.loadNotionDatabase(notiondb_dir)

    def notion_sheet(*_):
        base_path = os.sep.join(root_path.split(os.sep)[:-1]).replace('\\','/')
        nt_csv_dir = base_path + '/production_rec/notionDatabase/csv'
        csv_path_list = [nt_csv_dir + '/' + i for i in os.listdir(nt_csv_dir) if '.csv' in i]
        #print(csv_path_list)
        for csv_path in csv_path_list:
            sheet_dest_name = 'nt_{}'.format(csv_path.split('/')[-1].split('.')[0])
            print('upload destination sheet', sheet_dest_name)
            try:
                gSheet.updateFromCSV(csv_path, sheet_dest_name)
            except:
                print('can\'t upload dataframe to sheet {}'.format(sheet_dest_name))

class data:
    history_dir_name = '_history'

    def create_history(*_):
        for root, dirs, files in os.walk(rec_dir, topdown=False):
            for name in files:
                ext = '.csv'
                if not ext in name:
                    continue
                if data.history_dir_name in root:
                    continue
                file_path = os.path.join(root, name)

                hist_dir_path = os.path.join(root, data.history_dir_name)
                if not os.path.exists(hist_dir_path):
                    os.mkdir(hist_dir_path)

                mtime = os.stat(file_path).st_mtime
                mtime_hour = dt.datetime.fromtimestamp(mtime).hour
                mtime_srtftime = dt.datetime.fromtimestamp(mtime).strftime('%Y%m%d_00')
                if mtime_hour > 12:
                    mtime_srtftime = dt.datetime.fromtimestamp(mtime).strftime('%Y%m%d_01')

                hist_file_path = os.path.join(
                    hist_dir_path, name.replace(ext, '_{}{}'.format(mtime_srtftime, ext)))

                print(os.system('cls||clear'))
                print('create history  ', hist_file_path.split(os.sep)[-1])
                shutil.copyfile(file_path, hist_file_path)

    def clear_past_history(*_):
        for root, dirs, files in os.walk(rec_dir, topdown=False):
            for name in files:
                ext = '.csv'
                if not ext in name:
                    continue
                if data.history_dir_name in root:
                    continue
                file_path = os.path.join(root, name)

                hist_dir_path = os.path.join(root, data.history_dir_name)
                name_no_ext = name.replace(ext,'')

                hist_file_list = sorted([ i for i in os.listdir(hist_dir_path) if name_no_ext in i ])

                file_limit = 5
                if len(hist_file_list) > file_limit:
                    del_file_list = hist_file_list[:-file_limit]
                    keep_file_list = hist_file_list[-file_limit:]
                    #print(del_file_list , keep_file_list)
                    del_path_list = [ os.path.join(hist_dir_path, i) for i in del_file_list ]
                    for i in del_path_list:
                        del_file = del_file_list[del_path_list.index(i)]
                        print('remove off-limit[{}] history files'.format(file_limit), del_file)
                        os.remove(i)

    @staticmethod
    def get_history_path_list(file_path):
        ext = '.csv'
        file_path = file_path.replace('/',os.sep)
        name = os.path.basename(file_path)
        name_no_ext = name.replace(ext,'')
        file_dir = os.path.dirname(file_path)
        hist_dir_path = file_dir + os.sep + data.history_dir_name
        hist_file_list = sorted([ i for i in os.listdir(hist_dir_path) if name_no_ext in i ])
        hist_path_list = [os.path.join(hist_dir_path, i) for i in hist_file_list]
        return hist_path_list

class error:
    file_path = rec_dir + '/main_traceback.csv'

    @staticmethod
    def record(text):
        try:
            data = {
                'date_time': dt.datetime.now().strftime('%m-%d-%Y %H:%M:%S'),
                'traceback' : str(text)
            }
            error.file_path = rec_dir + '/main_traceback.csv'

            df = pd.DataFrame()
            if os.path.exists(error.file_path):
                df = pd.read_csv(error.file_path)
            df = df.append(pd.DataFrame.from_records([data]))
            df.reset_index(inplace=True, drop=True)
            df.to_csv(error.file_path, index=False)
        except:
            pass

    @staticmethod
    def get_nortify(clear_after = True):
        if os.path.exists(error.file_path):
            df = pd.read_csv(error.file_path)
            df.drop_duplicates(['traceback'], inplace=True)
            rec = []
            for i in df.index.tolist():
                row = df.loc[i]
                rec.append(row.to_dict())
            if clear_after:
                os.remove(error.file_path)
            return rec
        else:
            return []

class fika: #teletubbies files
    @staticmethod
    def cache_layout_file():
        dir_path = r'C:\Fika\Projects\Dug\Shots\Publish'
        dest_dir_path = r'D:\GDrive\Temp\Fika\Works\Layout'

        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                dest_file_path = os.path.join(dest_dir_path, name)

                if not '_Layout.ma' in name:
                    continue

                is_exists = os.path.exists(dest_file_path)

                if not is_exists:
                    shutil.copyfile(file_path, dest_file_path)
                    print(file_path)

    @staticmethod
    def ttf_ma_stat(limit_count = 15):

        vpn_log = open(r"C:\Users\DEX3D_I7\OpenVPN\log\GPLpfSenseA-UDP4-1196-fika_guest_3-config.log").readlines()
        #if not 'Initialization Sequence Completed' in vpn_log[-1]:
            #return None
        print('Fika Connection : {}'.format(vpn_log[-1]))

        stat_json_dir = r'D:\GDrive\Temp\Fika\Stat\json'

        all_ma_path_list = []
        ep_list = ['1015','1016','1017','1013','1014']
        for ep in ep_list:
            ep_path = r'E:\Shots\Publish\{}'.format(ep)
            try:
                seq_list = os.listdir(ep_path)
                seq_list = [i for i in seq_list if not '.' in i]
            except:
                return None

            for seq in seq_list:
                seq_path = ep_path + os.sep + seq
                shot_list = os.listdir(seq_path)
                #print(seq_path)
                #shot_dir = seq_path + os.sep + seq
                shot_path_list = [seq_path + os.sep + i for i in os.listdir(seq_path)]
                #print(shot_path_list)
                for s_path in shot_path_list:
                    shot = os.path.basename(s_path)
                    if '.' in shot: continue;
                    ma_path_list = [f'{s_path}/{st}/' + f'{ep}_{seq}_{shot}_{st}.ma' for st in os.listdir(s_path)]
                    ma_path_list = [i for i in ma_path_list if os.path.exists(i)]
                    #print(ma_path_list)
                    all_ma_path_list += ma_path_list
                    print(os.system('cls||clear'))
                    print('ma files ', len(all_ma_path_list), ' - ', end='')
                    for i in range(len(all_ma_path_list)):
                        if i % 15 == 0:
                            print('|', end='')
                    print('')
                #break
            #break

        load_count = 0
        for ma_path in all_ma_path_list:
            dir_path = os.path.dirname(ma_path).replace('.ma','')
            name = os.path.basename(ma_path)
            version = sorted([i for i in os.listdir(dir_path) if not '.' in i])
            if version != []:
                version = version[-1]
            else:
                version = 'v000'
            ep = name.split('_')[0]
            seq = name.split('_')[1]
            shot = name.split('_')[2]
            stage = name.split('_')[3]

            j_path = stat_json_dir + f'/{name}_{version}.json'.replace('.ma', '')
            if os.path.exists(j_path):
                continue
            if load_count > 15:
                return None

            print('record stat {}'.format(name), end='')
            data = maReader.getStat(ma_path)
            if data == None:
                continue
            data['name'] = name
            data['version'] = version
            data['episode'] = ep
            data['sequence'] = seq
            data['shot'] = shot
            data['stage'] = stage
            data['publish_dir'] = f'file:///E:/Shots/Publish/{ep}/{seq}/{shot}/{stage}/'

            with open(j_path, 'w') as j_file:
                json.dump(data, j_file, indent=4)
            load_count += 1

            print('    finished!')

    @staticmethod
    def stat_upload():
        df = pd.DataFrame()
        stat_json_dir = r'D:\GDrive\Temp\Fika\Stat\json'
        stat_path_list = [stat_json_dir + os.sep + i for i in os.listdir(stat_json_dir)]

        for j_path in stat_path_list:
            #print(j_path)
            data = json.load(open(j_path))
            df = df.append(pd.DataFrame([data]))
        df.reset_index(inplace=True, drop=True)

        csv_path = r'D:\GDrive\Temp\Fika\Stat'+os.sep+'ttf_version_stat.csv'
        df.to_csv(csv_path, index=False)

        time.sleep(5)
        gSheet.updateFromCSV(csv_path, 'ma_stat', newline='', sheet_name='Fika_TTF_Stat')
        print('update fika sheet')

    @staticmethod
    def studio_library():
        src_path = r'E:\Maya\AnimationTools\StudioLibrary'
        dst_path = r'X:\Server\StudioLibrary\Teletubies'
        for root, dirs, files in os.walk(src_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                dst_copy_path = os.path.dirname(file_path).replace(src_path,dst_path) + os.sep + os.path.basename(file_path)
                dst_folder_path = os.path.dirname(dst_copy_path)
                print(dst_copy_path)

                if not os.path.exists(dst_folder_path):
                    os.makedirs(dst_folder_path)
                if not os.path.exists(dst_copy_path):
                    shutil.copy(file_path, dst_copy_path)

    """
    def cache_audio_file():
        dir_path = r'E:\Mocap'
        dest_dir_path = r'D:\GDrive\Temp\Fika\Works\Layout'

        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                dest_file_path = os.path.join(dest_dir_path, name)

                if not 'Combined.wav' in name:
                    continue

                print(dirs,file_path)

                is_exists = os.path.exists(dest_file_path)

                if not is_exists:pass
                    #shutil.copyfile(file_path, dest_file_path)

    """


if __name__ == '__main__':
    #base_path = os.sep.join(root_path.split(os.sep)[:-1])
    #workspaceSetup()
    #versionBackup('.ma', base_path)
    #integration.init_notion_db()
    #integration.load_notion_db()
    #integration.notion_sheet()
    #data.create_history()
    #data.clear_past_history()
    #print(data.get_history_path_list(r"D:\GDrive\Documents\2022\BRSAnimPipeline\work\NodeProject\NodeProject\production_rec\notionDatabase\csv\project.csv"))

    #fika.cache_layout_file()
    #fika.cache_audio_file()
    #fika.ttf_ma_stat()
    #fika.stat_upload()
    fika.studio_library()
    pass