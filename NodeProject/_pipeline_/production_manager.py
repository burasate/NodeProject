# -*- coding: utf-8 -*-
import json,os,pprint,sys,time,shutil,requests
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
import numpy as np
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
from gSheet import gSheet
gSheet.sheetName = 'Node Project Integration'
from notionDatabase import notionDatabase
from gSheet import gSheet

# Path
prev_dir = os.sep.join(rootPath.split(os.sep)[:-1])
rec_dir = prev_dir + '/production_rec'
notiondb_dir = rec_dir + '/notionDatabase'
file_storage_dir = prev_dir + '/file_storage'

# Any Func
def load_worksheet(sheet, dirPath):
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

# Finance System
class finance:
    #from gSheet import gSheet as gSheet
    #gSheet.sheetName = 'KF_Personal_FlowAccount'
    flow_account_sheet = 'KF_Personal_FlowAccount'

    @staticmethod
    def generate_document():
        """
        project_id = 'c3193d9b885043f89cc51c5a0508a1a6'
        member_name = 'Kaofang.B71'
        doc_type = 'quotation'
        """
        channel_id = task_queue.data['channel_id']
        member_name = task_queue.data['member_name']
        doc_type = task_queue.data['document_type']

        #old_sheet_name = gSheet.sheetName
        #gSheet.sheetName = 'KF_Personal_FlowAccount'
        config_sheet = 'config'

        nt_project_path = notiondb_dir + '/csv' + '/project.csv'
        project_df = pd.read_csv(nt_project_path)

        #print(project_df)
        project_df = project_df[project_df['discord_channel_id'] == channel_id]
        if project_df.empty:
            raise Warning('Not Found Project')
            return None
        #print(project_df.loc[project_df.index.tolist()[0]])
        project_sl = project_df.loc[project_df.index.tolist()[0]]
        project_finance = project_sl['finance']
        #print(project_finance, 'nan', project_finance is np.nan)
        if project_finance is np.nan:
            raise Warning('Not Found Project Finance')
            return None

        nt_finance_path = notiondb_dir + '/csv' + '/project_finance.csv'
        finance_df = pd.read_csv(nt_finance_path)
        #print(finance_df)
        finance_df = finance_df[finance_df['title'] == project_finance]
        finance_sl = finance_df.loc[finance_df.index.tolist()[0]]
        #print(finance_sl)

        #Price
        finance_sl['service_unit_price'] = finance_sl['service_unit_price'] * finance_sl['service_quantity']
        finance_sl['service_quantity'] = 1
        workload_percentile = project.get_member_workload(project_sl['project_name'], member_name)
        finance_sl['service_unit_price'] = finance_sl['service_unit_price'] * workload_percentile
        finance_sl['service_unit_price'] = finance_sl['service_unit_price'].round(0)

        finance_config = gSheet.getAllDataS('config', sheet_name=finance.flow_account_sheet)

        nt_member_path = notiondb_dir + '/csv' + '/member.csv'
        member_df = pd.read_csv(nt_member_path)
        member_df = member_df[member_df['member_name'] == member_name]
        if member_df.empty:
            return None
        member_sl = member_df.loc[member_df.index.tolist()[0]]
        #print(member_sl)

        member_data = {
            'company_name' : member_sl['bank_account_name'],
            'company_address' : member_sl['address'],
            'company_tax_id' : '{:0>13d}'.format(int(member_sl['tax_id'])),
            'company_mobile' : '{:0>10d}'.format(int(member_sl['mobile'])),
            'bank_account_name' : member_sl['bank_account_name'],
            'bank_company_name' : member_sl['bank_company_name'],
            'bank_account_number' : '{:0>10d}'.format(int(member_sl['bank_account_number']))
        }

        link_data = {}
        for i in finance_config:
            prop_name, prop_value = (i['property_name'], i['property_value'])
            if prop_name in ['quotation_pdf_url','billing_pdf_url','invoice_pdf_url']:
                link_data[prop_name] = prop_value

            if i['is_formula'] == 'TRUE':
                continue

            #print(prop_name, [prop_name in finance_df.columns])

            if prop_name in member_data:
                #'''
                gSheet.setValue(
                    config_sheet, findKey='property_name', findValue=prop_name,
                    key='property_value', value=str(member_data[prop_name]),
                    sheet_name=finance.flow_account_sheet
                )
                #'''
            elif prop_name in finance_df.columns:
                #'''
                gSheet.setValue(
                    config_sheet, findKey = 'property_name', findValue = prop_name,
                    key = 'property_value', value=str(finance_sl[prop_name]),
                    sheet_name=finance.flow_account_sheet
                )
                #'''
            time.sleep(2)

        #Finish GSheet
        #fin_gSheet.sheetName = old_sheet_name
        pprint.pprint(link_data)

        #Save file
        url = link_data[doc_type + '_pdf_url']
        res = requests.get(url)
        project_dir = file_storage_dir + os.sep + project_sl['page_id']
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        pdf_path = project_dir + '/{}_{}.pdf'.format(member_sl['page_id'],doc_type)
        with open(pdf_path, 'wb') as f:
            f.write(res.content)
            print('pdf exprted {}'.format(pdf_path.replace(project_dir,'')))

    @staticmethod
    def auto_generate_document():
        flow_account_rec = gSheet.getAllDataS('FlowAccount')
        #pprint.pprint(flow_account_rec)

        for data in flow_account_rec:
            if data['request_count'] == 1:
                continue
            if data['timestamp'] == '':
                continue

            #pprint.pprint(data)
            data_new = {}
            for i in data:
                data_new[i.strip().replace(' ','_').lower()] = data[i]
            pprint.pprint(data_new)

            nt_member_path = notiondb_dir + '/csv' + '/member.csv'
            member_df = pd.read_csv(nt_member_path)
            member_df = member_df[member_df['member_name'] == data['Member Name']]
            if member_df.empty:
                raise Warning('Not found member name\nPlease check member name is correct')
            member_sl = member_df.loc[member_df.index.tolist()[0]]
            #print(member_sl)
            member_data = {
                'company_name': member_sl['bank_account_name'],
                'company_address': member_sl['address'],
                'company_tax_id': '{:0>13d}'.format(int(member_sl['tax_id'])),
                'company_mobile': '{:0>10d}'.format(int(member_sl['mobile'])),
                'bank_account_name': member_sl['bank_account_name'],
                'bank_company_name': member_sl['bank_company_name'],
                'bank_account_number': '{:0>10d}'.format(int(member_sl['bank_account_number']))
            }

            finance_config = gSheet.getAllDataS('config', sheet_name=finance.flow_account_sheet)
            for i in finance_config:
                prop_name, prop_value = (i['property_name'], i['property_value'])
                if i['is_formula'] == 'TRUE':
                    continue
                if prop_name in member_data:
                    value = ''
                    if not str(prop_value) == str(member_data[prop_name]):
                        #print(str(member_data[prop_name]))
                        gSheet.setValue(
                            'config', findKey='property_name', findValue=prop_name,
                            key='property_value', value=str(member_data[prop_name]),
                            sheet_name=finance.flow_account_sheet
                        )
                        time.sleep(2)
                elif prop_name in list(data_new):
                    if not str(prop_value) == str(data_new[prop_name]):
                        #print(str(data_new[prop_name]))
                        gSheet.setValue(
                            'config', findKey='property_name', findValue=prop_name,
                            key='property_value', value=str(data_new[prop_name]),
                            sheet_name=finance.flow_account_sheet
                        )
                        time.sleep(2)


            pdf_url = [i for i in finance_config
                       if i['property_name'] == f'''{data_new['document_type']}_pdf_url'''
                       ][0]['property_value']
            #print(pdf_url)

            #Save file
            res = requests.get(pdf_url)
            project_dir = file_storage_dir + os.sep + data_new['project_id']
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
            pdf_path = project_dir + '/{}_{}.pdf'.format(member_sl['page_id'], data_new['document_type'])
            with open(pdf_path, 'wb') as f:
                f.write(res.content)
                print('pdf exprted {}'.format(os.path.basename(pdf_path)))

            #'''
            if data['request_count'] != 1:
                gSheet.setValue('FlowAccount', findKey='Timestamp', findValue=data['Timestamp'],
                                key='request_count', value=1)
            elif data['request_count'] <= 1:
                continue
            #'''

            #Update Financial Data
            dst_db_id = [i['id'] for i in notionDatabase.database if i['name'] == 'project_finance'][0]
            db_data = notionDatabase.getDatabase(dst_db_id)
            #pprint.pprint(db_data['results'])
            id_list = [i['id'] for i in db_data['results']]
            title_list = []
            print('reading title name')
            for page_id in [i['id'] for i in db_data['results']]:
                title = notionDatabase.getPageProperty(page_id, 'title')['results'][0]['title']['text']['content']
                title_list.append(title)
            #print(title_list)

            if data_new['project_name'] in title_list:
                index = title_list.index(data_new['project_name'])
                new_page = notionDatabase.getPage(id_list[index])
            else:
                new_page = notionDatabase.createPage(dst_db_id, 'title', data_new['project_name'])

            #pprint.pprint(new_page)
            prop_list = [i for i in new_page['properties'] if i in data_new]
            for prop_name in prop_list:
                new_page_id = new_page['id'].replace('-', '')
                try:
                    notionDatabase.updatePageProperty(new_page_id, prop_name, data_new[prop_name])
                except:pass
            notionDatabase.updatePageProperty(new_page['id'], 'project_name',
                                              [data_new['project_id']])

    def get_document_review():
        doc_data = gSheet.getAllDataS('Document')
        #pprint.pprint(doc_data)
        r_data = []
        for data in doc_data:
            if data['request_count'] == '':
                data['request_count'] = 0
            if not data['document_type'] == 'financial':
                continue
            if data['request_count'] > 0:
                continue

            #print(data)
            data['request_count'] += 1
            gSheet.setValue('Document', findKey='Timestamp', findValue=data['Timestamp'],
                            key='request_count', value=data['request_count'])
            r_data.append(data)

        return r_data

# Member System
class register:
    def update_member(*_):
        regis_sheet = 'Registration'
        regis_path = '{}/{}.json'.format(rec_dir,regis_sheet)
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'
        dest_db_id = [i['id'] for i in notionDatabase.database if i['name'] == 'member'][0]

        #load online database
        load_worksheet(regis_sheet, rec_dir)

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
            nick = str(row['Nick Name']).capitalize()
            if ' ' in row['Nick Name']:
                for i in range(3):
                    nick = nick.replace(' ','')

                gSheet.setValue(
                    regis_sheet, findKey='Discord ID', findValue=discord_id,
                    key='Nick Name', value=nick
                )

            #member_name = '.'.join([ nick.capitalize(), row['First Name'][0].upper() + str(discord_id)[-2:]])
            member_name = '{}.{}{}'.format(
                nick.capitalize(),
                str(row['First Name'][0]).upper(),
                str(discord_id)[-2:]
            )
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

            #Address	Bank Account Name	Mobile	Bank Account Number	Bank Company Name	Tax Id
            prop_dict = {
                'discord_id': int(discord_id),
                'demo_reel': row['Demo Reel'],
                'email': row['Email Address'],
                'first_name': row['First Name'].capitalize(),
                'last_name': row['Last Name'].capitalize(),
                'hour_per_week': float(hour_per_week),
                'linkedin': row['Linkedin Profile'],
                'address': str(row['Address']).replace('\n', ' '),
                'bank_account_name': row['Bank Account Name'],
                'mobile': row['Mobile'],
                'bank_account_number': row['Bank Account Number'],
                'bank_company_name': row['Bank Company Name'],
                'tax_id': row['Tax Id']
            }
            #pprint.pprint(prop_dict)

            # Load Notion Database
            dst_db_id = [i['id'] for i in notionDatabase.database if i['name'] == 'member'][0]
            db_filter = {
                'property' : 'title',
                'rich_text' : {
                    'contains' : member_name
                }
            }
            db_data = notionDatabase.getDatabase(dst_db_id, filter=db_filter)
            id_list = [i['id'] for i in db_data['results']]
            title_list = []
            for page_id in [i['id'] for i in db_data['results']]:
                title = notionDatabase.getPageProperty(page_id, 'title')['results'][0]['title']['text']['content']
                title_list.append(title)

            #print('Find Exist Member in Database')
            print(title_list, id_list)

            #'''
            # Add New Member
            #if not member_name in member_df['member_name'].tolist():
            if not member_name in title_list:
                new_page = notionDatabase.createPage(dest_db_id,'member_name', member_name)
                for prop_name in prop_dict:
                    new_page_id = new_page['id'].replace('-','')
                    try:
                        notionDatabase.updatePageProperty(new_page_id, prop_name, prop_dict[prop_name])
                    except:pass
            # Update Member
            #if member_name in member_df['member_name'].tolist():
            elif member_name in title_list:
                find_index = member_df[member_df['member_name'] == member_name].index.tolist()[0]
                find_row = member_df.loc[find_index]
                for prop_name in prop_dict:
                    v = prop_dict[prop_name]
                    if v == '':
                        continue
                    if str(v) == '' and prop_name in ['demo_reel','linkedin']: #url format
                        v = '-'
                    if prop_dict[prop_name] != find_row[prop_name]:
                        try:
                            notionDatabase.updatePageProperty(find_row['page_id'], prop_name, v)
                        except:pass
            #'''

            #break

# Project System
class project:
    '''
    def update_invite(*_):
        nt_project_path = notiondb_dir + '/csv' + '/project.csv'
        nt_member_path = notiondb_dir + '/csv' + '/member.csv'

        project_df = pd.read_csv(nt_project_path)
        member_df = pd.read_csv(nt_member_path)

        #print(project_df)
        for i in project_df.index.tolist():
            row = project_df.loc[i]
            #if not row['title'] in ['Ingma','Project Test']:
                #continue
            #print(row)

            ready_to_invite = row['ready_to_invite']
            sent_invite = row['sent_invite']

            if ready_to_invite and not sent_invite:
                notionDatabase.updatePageProperty(row['page_id'], 'sent_invite', True)
    '''

    def add_project_member(*_):
        discord_id = task_queue.data['discord_id']
        project_name = task_queue.data['project_name']
        hour_week = task_queue.data['hour_week']

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

        project_member_df['project_name'] = project_member_df['project_name'].str.strip()
        project_member_df['project_name'] = project_member_df['project_name'].str.replace(' ', '_')
        project_member_df['project_name'] = project_member_df['project_name'].str.lower()
        #print(project_member_df)

        is_exists = False
        for i in project_member_df.index.tolist():
            row = project_member_df.loc[i]
            is_exists = (
                row['member_name'] == member_sl['title'] and
                row['project_name'] == project_sl['title']
            )
            if is_exists:
                notionDatabase.updatePageProperty(row['page_id'], 'member', member_sl['page_id'])
                notionDatabase.updatePageProperty(row['page_id'], 'project', project_sl['page_id'])

        if not is_exists:
            new_page = notionDatabase.createPage(dest_db_id, 'member_name', member_sl['title'])
            notionDatabase.updatePageProperty(new_page['id'], 'member', member_sl['page_id'])
            notionDatabase.updatePageProperty(new_page['id'], 'project_name', project_sl['page_id'])

            gSheet.setValue(
                regis_sheet, findKey='Discord ID', findValue=discord_id,
                key='Availability', value= round((regis_sl['Availability'] + hour_week) * 0.5)
            )

            project_member_df = project_member_df.append(pd.DataFrame.from_records([{
                'page_id' : new_page['id'], 'member': member_sl['page_id'],
                'project_name' : project_sl['page_id'], 'hour_week' : hour_week
            }]))

        project_member_df.reset_index(drop=True, inplace=True)
        project_member_df.to_csv(nt_project_member_path, index=False)

    @staticmethod
    def get_member_workload(project_name, member_name, percentile=True):
        nt_project_member_path = notiondb_dir + '/csv' + '/project_member.csv'
        pm_df = pd.read_csv(nt_project_member_path)
        pm_df = pm_df[pm_df['project_name'] == project_name]
        if pm_df.empty:
            return 0.0
        #print(pm_df)

        sec_total = pm_df['second_duration'].sum()
        if sec_total == 0.0:
            raise Warning('total second duration error {}\nplease check you data or assignment'.format(sec_total))
        sec_dur = pm_df[pm_df['member_name'] == member_name]['second_duration'].sum()
        #print(sec_dur, sec_total, sec_dur/sec_total)

        if percentile:
            return round(sec_dur/sec_total,2)
        else:
            return sec_dur

# Task System
class task_queue:
    data = {}
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
        if os.name == 'nt':
            return None
        request_sheet = 'Request'
        request_path = '{}/{}.json'.format(rec_dir,request_sheet)
        load_worksheet(request_sheet, rec_dir)

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
                if row['name'] == '':
                    pass

                elif row['name'] == 'sent_invite_to_project':
                    project.update_invite()

                elif row['name'] == 'set_project_channel_id':
                    task_queue.set_project_channel_id()

                elif row['name'] == 'join_project':
                    project.add_project_member()

                elif row['name'] == 'generate_financial_document':
                    print('financial document - clear request quota...')
                    time.sleep(30)
                    finance.generate_document()

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

    import system_manager
    #system_manager.integration.init_notion_db()
    #system_manager.integration.load_notion_db()
    #system_manager.integration.notion_sheet()

    #load_worksheet('AnimationTracking', base_path + '/production_rec')
    #finance.get_finance_doc_link()
    #finance.get_document_review()
    #finance.auto_generate_document()
    #print(project.get_member_workload('Ailynn AIS', 'Kaofang.B71'))
    #project.get_member_workload('Financial_test1', 'Kaofang.B71')

    register.update_member()
    #task_queue.run()
    #project.update_invite()
    #project.add_member(346164580487004171, 'Project_Test', 20)
    pass

    #loadNotionDatabase(base_path + '/production_rec/notionDatabase')