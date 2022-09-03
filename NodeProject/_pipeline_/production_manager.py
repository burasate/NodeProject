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

# Any Func
def loadWorksheet(sheet, dirPath):
    data = gSheet.getAllDataS(sheet)
    savePath = dirPath + os.sep + sheet + '.json'
    json.dump(data, open(savePath, 'w'), indent=4)
    print('Load worksheet {} - {}'.format(gSheet.sheetName,sheet))
"""
def loadNotionDatabase(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    notionDatabase.loadNotionDatabase(dirPath)
"""

# Member System
class register:
    def update_member(*_):
        regis_sheet = 'Registration'
        regis_path = '{}/{}.json'.format(rec_dir,regis_sheet)
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'
        dest_db_id = [i['id'] for i in notionDatabase.database if i['name'] == 'member'][0]

        #load online database
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
            discord_id = row['Discord ID']
            member_name = '.'.join([ row['Nick Name'].capitalize(), row['First Name'][0].upper() + str(discord_id)[-2:]])
            #print(member_name, row['Discord ID'])

            hour_per_week = ''.join([i for i in str(row['Availability']) if i.isdigit() or i == '-' or i == '.'])
            hour_per_week_split = [float(i) for i in hour_per_week.split('-')]
            #print(hour_per_week_split)
            if len(hour_per_week_split) == 2:
                hour_per_week = (hour_per_week_split[0]+hour_per_week_split[-1])*0.5
                hour_per_week = round(hour_per_week)
            #print(str(hour_per_week), str(row['Availability']))
            #print(str(hour_per_week) != str(row['Availability']))
            if str(hour_per_week) != str(row['Availability']):
                gSheet.setValue(
                    regis_sheet, findKey='Discord ID', findValue=discord_id,
                    key='Availability', value=hour_per_week
                )

            prop_dict = {
                'discord_id': int(discord_id),
                'demo_reel': row['Demo Reel'],
                'email': row['Email Address'],
                'first_name': row['First Name'].capitalize(),
                'last_name': row['Last Name'].capitalize(),
                'hour_per_week': float(hour_per_week),
                'linkedin': row['Linkedin Profile']
            }

            # Add New Member
            if not member_name in member_df['member_name'].tolist():
                new_page = notionDatabase.createPage(dest_db_id,'member_name', member_name)
                """
                for prop_name in prop_dict:
                    new_page_id = new_page['id'].replace('-','')
                    notionDatabase.updatePageProperty(new_page_id, prop_name, prop_dict[prop_name])
                """
            # Update Member
            if member_name in member_df['member_name'].tolist():
                find_index = member_df[member_df['member_name'] == member_name].index.tolist()[0]
                find_row = member_df.loc[find_index]
                for prop_name in prop_dict:
                    v = prop_dict[prop_name]
                    if str(v) == '' and prop_name in ['demo_reel','linkedin']: #url format
                        v = '-'
                    if prop_dict[prop_name] != find_row[prop_name]:
                        notionDatabase.updatePageProperty(find_row['page_id'], prop_name, v)

# Project System
class project:
    def update_invite(*_):
        nt_project_path = notiondb_dir + '/csv' + '/project.csv'
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'

        project_df = pd.read_csv(nt_project_path)
        member_df = pd.read_csv(nt_member_path)

        #print(project_df)
        for i in project_df.index.tolist():
            row = project_df.loc[i]
            if not row['title'] in ['Ingma','Project Test']:
                continue
            #print(row)

            ready_to_invite = row['ready_to_invite']
            sent_invite = row['sent_invite']

            if ready_to_invite and not sent_invite:
                notionDatabase.updatePageProperty(row['page_id'], 'sent_invite', True)

    def add_member(discord_id, project_name, hour_week):
        regis_sheet = 'Registration'
        regis_path = '{}/{}.json'.format(rec_dir, regis_sheet)
        regis_json = json.load(open(regis_path))
        nt_project_path = notiondb_dir + '/csv' + '/project.csv'
        nt_project_member_path = notiondb_dir + '/csv' + '/project_member.csv'
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'
        dest_db_id = [i['id'] for i in notionDatabase.database if i['name'] == 'project_member'][0]

        regis_df = pd.DataFrame().from_records(regis_json)
        project_df = pd.read_csv(nt_project_path)
        project_member_df = pd.read_csv(nt_project_member_path)
        member_df = pd.read_csv(nt_member_path)

        regis_df = regis_df[regis_df['Discord ID'] == discord_id]
        if regis_df.empty:
            raise Warning('cannot found discord id {} in register'.format(discord_id))
        regis_index = regis_df.index.tolist()[0]
        regis_sl = regis_df.loc[regis_index]

        member_df = member_df[member_df['discord_id'] == discord_id]
        if member_df.empty:
            raise Warning('cannot found discord id {} in member'.format(discord_id))
        member_index = member_df.index.tolist()[0]
        member_sl = member_df.loc[member_index]
        #print(member_sl)

        project_name = project_name.strip().replace(' ','_').lower()
        project_df['title'] = project_df['title'].str.strip()
        project_df['title'] = project_df['title'].str.replace(' ','_')
        project_df['title'] = project_df['title'].str.lower()
        project_df = project_df[project_df['title'] == project_name]
        if project_df.empty:
            raise Warning('cannot found project name {} in project'.format(project_name))
        project_index = project_df.index.tolist()[0]
        project_sl = project_df.loc[project_index]
        #print(project_sl)

        project_member_df['project'] = project_member_df['project'].str.strip()
        project_member_df['project'] = project_member_df['project'].str.replace(' ', '_')
        project_member_df['project'] = project_member_df['project'].str.lower()
        #print(project_member_df)

        is_exists = False
        for i in project_member_df.index.tolist():
            row = project_member_df.loc[i]
            is_exists = (
                row['member_name'] == member_sl['title'] and
                row['project'] == project_sl['title']
            )
            if is_exists:
                notionDatabase.updatePageProperty(row['page_id'], 'member', member_sl['page_id'])
                notionDatabase.updatePageProperty(row['page_id'], 'project', project_sl['page_id'])
                notionDatabase.updatePageProperty(row['page_id'], 'hour_week', hour_week)

        if not is_exists:
            new_page = notionDatabase.createPage(dest_db_id, 'member_name', member_sl['title'])
            notionDatabase.updatePageProperty(new_page['id'], 'member', member_sl['page_id'])
            notionDatabase.updatePageProperty(new_page['id'], 'project', project_sl['page_id'])
            notionDatabase.updatePageProperty(new_page['id'], 'hour_week', hour_week)

            gSheet.setValue(
                regis_sheet, findKey='Discord ID', findValue=discord_id,
                key='Availability', value= round((regis_sl['Availability'] + hour_week) * 0.5)
            )

            project_member_df = project_member_df.append(pd.DataFrame.from_records([{
                'page_id' : new_page['id'], 'member': member_sl['page_id'],
                'project' : project_sl['page_id'], 'hour_week' : hour_week
            }]))

        project_member_df.reset_index(drop=True, inplace=True)
        project_member_df.to_csv(nt_project_member_path, index=False)

# Task System
class task_queue:
    data = {}
    def task_pucnch(*_):
        print('do punch task {}'.format(task_queue.data['who']))
        print('oraa \n'*10)

    def set_project_channel_id():
        task_queue.data
        notionDatabase.updatePageProperty(
            task_queue.data['project_id'],
            'discord_channel_id',
            task_queue.data['channel_id']
        )

    '''
    def sent_role_welcome_update(data):
        #task_queue.data['id_list']
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'
        member_df = pd.read_csv(nt_member_path)
        #print(member_df)

        for i in member_df.index.tolist():
            row = member_df.loc[i]
            if row['discord_id'] in data['id_list']:
                notionDatabase.updatePageProperty(row['page_id'], 'sent_role_welcome', True)
    '''

    def run(*_):
        request_sheet = 'Request'
        request_path = '{}/{}.json'.format(rec_dir,request_sheet)
        loadWorksheet(request_sheet, rec_dir)

        request_json = json.load(open(request_path))
        request_df = pd.DataFrame().from_records(request_json)
        request_df.sort_values(by=['date_time'], ascending=[True], inplace=True)
        for i in request_df.index.tolist():
            row = request_df.loc[i]
            print('Get Task  ', row.to_dict())
            task_queue.data = json.loads(str(row['data']).replace('\'','\"'))

            if 'error' in task_queue.data:
                task_queue.data['error'] == ''
            #print(task_queue.data)

            clear = True
            try:
                if row['name'] == 'punch':
                    task_queue.task_pucnch()

                elif row['name'] == 'sent_invite_to_project':
                    project.update_invite()

                elif row['name'] == 'set_project_channel_id':
                    task_queue.set_project_channel_id()

                elif row['name'] == 'join_project':
                    project.add_member(
                        task_queue.data['discord_id'],
                        task_queue.data['project_name'],
                        task_queue.data['hour_week']
                    )

                else:
                    clear = False

                # Clear Task
                if clear:
                    gSheet.deleteRow(request_sheet, 'date_time', row['date_time'])
                    #break #Loop per Task

            except Exception as e:
                import traceback
                print(str(traceback.format_exc()))
                gSheet.setValue(
                    request_sheet, findKey='date_time', findValue=row['date_time'],
                    key='error', value=str(traceback.format_exc())
                )
                now = str(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                gSheet.setValue(
                    request_sheet, findKey='date_time', findValue=row['date_time'],
                    key='date_time', value=now
                )

if __name__ == '__main__':
    base_path = os.sep.join(rootPath.split(os.sep)[:-1])
    #loadWorksheet('AnimationTracking', base_path + '/production_rec')

    register.update_member()
    task_queue.run()
    #project.update_invite()
    #project.add_member(346164580487004171, 'Project_Test', 20)
    pass

    #loadNotionDatabase(base_path + '/production_rec/notionDatabase')