import json,os,pprint,sys,time,shutil
import datetime as dt

"""
Init
"""
rootPath = os.path.dirname(os.path.abspath(__file__))
srcPath = rootPath+'/src'
sitePackagePath = rootPath+'/src'+'/site-packages'

#Environment
if not rootPath in sys.path:
    sys.path.insert(0,rootPath)
if not srcPath in sys.path:
    sys.path.insert(0,srcPath)
if not sitePackagePath in sys.path:
    sys.path.insert(0,sitePackagePath)


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

# Any Func
def loadWorksheet(sheet, dirPath):
    data = gSheet.getAllDataS(sheet)
    savePath = dirPath + os.sep + sheet + '.json'
    json.dump(data, open(savePath, 'w'), indent=4)
    print('Load worksheet {} - {}'.format(gSheet.sheetName,sheet))

def loadNotionDatabase(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    notionDatabase.loadNotionDatabase(dirPath)

# Member System
class register:
    def updateMember(*_):
        regis_sheet = 'Registration'
        regis_path = '{}/{}.json'.format(rec_dir,regis_sheet)
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'
        db_member_id = [i['id'] for i in notionDatabase.database if i['name'] == 'member'][0]

        #load online database
        #loadNotionDatabase(notiondb_dir)
        loadWorksheet(regis_sheet, rec_dir)

        # Compare 2 Dataframes
        regis_json = json.load(open(regis_path))
        regis_df = pd.DataFrame().from_records(regis_json)
        member_df = pd.read_csv(nt_member_path)
        #print(regis_df)
        #print(member_df.head(1))
        for i in regis_df.index.tolist():
            row = regis_df.loc[i]
            #print(row)
            discord_id = str(row['Discord ID'])
            member_name = '.'.join([ row['Nick Name'].capitalize(), row['First Name'][0].upper() + discord_id[-2:], ])
            #print(member_name, row['Discord ID'])
            prop_dict = {
                'discord_id': int(discord_id),
                'demo_reel': row['Demo Reel'],
                'email': row['Email Address'],
                'first_name': row['First Name'].capitalize(),
                'last_name': row['Last Name'].capitalize(),
                'hour_per_week': float(row['Availability']),
                'linkedin': row['Linkedin Profile']
            }

            # Add New Member
            if not member_name in member_df['member_name'].tolist():
                new_page = notionDatabase.createPage(db_member_id,'member_name', member_name)
                for prop_name in prop_dict:
                    new_page_id = new_page['id'].replace('-','')
                    notionDatabase.updatePageProperty(new_page_id, prop_name, prop_dict[prop_name])
            # Update Member
            elif member_name in member_df['member_name'].tolist():
                find_index = member_df[member_df['member_name'] == member_name].index.tolist()[0]
                find_row = member_df.loc[find_index]
                for prop_name in prop_dict:
                    if prop_dict[prop_name] != find_row[prop_name]:
                        notionDatabase.updatePageProperty(find_row['page_id'], prop_name, prop_dict[prop_name])

# Task Sytem
class task:
    def task_pucnch():
        print('do punch task')
        print('oraa \n'*10)

    def test():
        request_sheet = 'Request'
        request_path = '{}/{}.json'.format(rec_dir,request_sheet)
        loadWorksheet(request_sheet, rec_dir)

        request_json = json.load(open(request_path))
        request_df = pd.DataFrame().from_records(request_json)
        for i in request_df.index.tolist():
            row = request_df.loc[i]

            if row['name'] == 'punch':
                task.task_pucnch()
                continue

            if row['name'] == 'punch':
                task.task_pucnch()
                continue

            #Clear Task
            #gSheet.deleteRow(request_sheet, 'date_time', row['date_time'])


if __name__ == '__main__':
    #mainPath = os.sep.join(rootPath.split(os.sep)[:-1])
    #loadWorksheet('AnimationTracking', mainPath + '/production_rec')
    #loadNotionDatabase(mainPath + '/production_rec/notionDatabase')
    #register.updateMember()
    task.test()

    pass