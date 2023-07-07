# -*- coding: utf-8 -*-
import json,os,pprint,sys,time,shutil,requests, random
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
            if data['Timestamp'] == '':
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
        regis_df = regis_df.sample(frac=1.0)
        regis_df.reset_index(drop=True, inplace=True)
        member_df = pd.read_csv(nt_member_path)

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

    @staticmethod
    def set_project_channel_id():
        notionDatabase.updatePageProperty(task_queue.data['project_id'], 'discord_channel_id',
                                          task_queue.data['channel_id'])

# Gumraod Data Pipline
class gumroad_script_tools:
    @staticmethod
    def test():
        ntdb = notionDatabase
        ntdb_id = 'fbca8d791aa54ac5b0d73a0766992295'
        data = task_queue.data
        pprint.pprint(data)
        db_filter = {
            'and': [
                {
                    'property': 'name',
                    'rich_text': {'equals': data['user_last']}
                },
                {
                    'property': 'ip',
                    'rich_text': {'equals': data['ip']}
                },
                {
                    'property': 'script_name',
                    'rich_text': {'equals': data['script_name']}
                },
            ]
        }
        db_data = ntdb.getDatabase(ntdb_id, filter=db_filter)
        is_page_empty = db_data['results'] == []
        print(db_data['results'])

        # Notion delete duplicated pages
        if len(db_data['results']) > 1:
            print('ununique   : {}'.format(len(db_data['results'])))
            for p in db_data['results'][1:]:
                ntdb.del_page_id(p['id'])

        # Notion page define
        if is_page_empty:  # New page
            page = ntdb.createPage(ntdb_id, 'name', data['user_last'])
        else:  # Update page
            page = db_data['results'][0]

        #properties used
        prop_ls = list(page['properties'])
        for p in list(data):
            if not p in prop_ls:
                del data[p]
        print('prepared data  ', data)

        # Notion page organise
        ntdb.update_page_properties(page['id'], data)
        #if is_page_empty:
            #pass
        #else:
            #pass

# Task System (Lastest decoration)
class task_queue:
    data = {}
    func_rec = [
        {
            'task_name': 'set_project_channel_id',
            'task_func': project.set_project_channel_id,
            'wait': 0.0
        },
        {
            'task_name': 'join_project',
            'task_func': project.add_project_member,
            'wait': 0.0
        },
        {
            'task_name': 'generate_financial_document',
            'task_func': finance.generate_document,
            'wait': 30.0
        },
        {
            'task_name': 'script_tool_check_in',
            'task_func': gumroad_script_tools.test,
            'wait': 0.0
        },
    ]

    @staticmethod
    def run(dev_mode=False):

        if os.name == 'nt' and not dev_mode:return None
        elif os.name == 'nt' and not __name__ == '__main__': return None

        request_sheet = 'Request'
        request_path = '{}/{}.json'.format(rec_dir,request_sheet)
        load_worksheet(request_sheet, rec_dir)

        request_json = json.load(open(request_path))
        request_df = pd.DataFrame().from_records(request_json)
        request_df.sort_values(by=['date_time'], ascending=[True], inplace=True)
        for i in request_df.index.tolist():
            row = request_df.loc[i]
            s_data = str(row['data']).replace('\'','\\\"')
            print('\nGet Task  {}'.format(i+1), s_data)
            task_queue.data = json.loads(s_data)

            if 'error' in task_queue.data:
                task_queue.data['error'] == ''
            #print(task_queue.data)

            clear = False
            if not row['name'] in [i['task_name'] for i in task_queue.func_rec]:
                continue
            func_idx = [i['task_name'] for i in task_queue.func_rec].index(row['name'])

            try:
                #Data
                print('Get Data  ', task_queue.data)

                #Excute
                task_queue.func_rec[func_idx]['task_func']()
                clear = True if not dev_mode else False

                '''
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
                '''

                #else:
                    #clear = False

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

class quote_daily:
    '''
    CG Quote Generator
    '''
    def __init__(self):
        from podcastListener import podcastListener
        self.pl = podcastListener.plistener(podcastListener.podcast_rss)
        self.transcription_dir = podcastListener.transcription_dir
        self.dc_cfg_path = rootPath + '/raspi_dcbot.json'
        self.dc_cfg = json.load(open(self.dc_cfg_path))
        self.dc_cfg['open_ai_gpt']['model'] = 'gpt-3.5-turbo'
        import openai
        self.openai = openai
        self.text_path_cache = []
        self.ntdb_id = 'c29a633124b94bfc88633f6da1f9ba71'
        #print(self.transcription_dir)
        #print(self.dc_cfg)
        #self.rec_dir

    def load_podcast_transcript(self):
        self.pl.cache_transcription_from_podcast_rss(count_limit=3)

    def get_rand_transcript_line(self):
        txt_path_ls = [self.transcription_dir + os.sep + i for i in os.listdir(self.transcription_dir)]
        files_total = len(txt_path_ls)
        if len(self.text_path_cache) == len(txt_path_ls):  # clear cache
            self.text_path_cache = []

        # select random latest
        txt_ctime_ls = [os.stat(i).st_ctime for i in txt_path_ls]
        txt_path_ls = [i[-1] for i in sorted(zip(txt_ctime_ls, txt_path_ls), reverse=True)]
        txt_path_ls = [i for i in txt_path_ls if not i in self.text_path_cache]
        #print(txt_ctime_ls)
        #print(json.dumps(txt_path_ls, indent=4))
        idx_sl = random.randint(0,len(txt_path_ls)-1)
        if idx_sl > 4:
            idx_sl = 4
        text_sl_path = txt_path_ls[idx_sl]

        self.text_path_cache.append(text_sl_path) #add to cache
        self.text_path_cache = self.text_path_cache[-1 * int(round(files_total * 0.75)):]

        # data
        file_name = os.path.basename(text_sl_path)
        title = file_name.replace('.txt','').replace('_',' ').replace('  ',' ').capitalize()
        with open(text_sl_path) as f:
            f_read = f.readlines()
            f_read = [i.replace('\n','') for i in f_read]
        #print(text_sl_path)
        #print(file_name)
        #print(title)
        #print(len(f_read))
        line_idx = random.randint(0,max(range(len(f_read))))
        line_num =  line_idx + 1

        print(round(len(self.text_path_cache)/files_total,1),
              [title.upper()], '{} / {}'.format(line_num,len(f_read)))

        data = {
            'title' : title,
            'file_name' : file_name,
            'line_number' : line_num,
            'content' : f_read[line_idx],
        }
        #pprint.pprint(data)
        return data

    def get_completion_response(self, message):
        system_prompt = '''
I want you summarize the viewport, perspective and attitude for a career of VFX, Game, Animation (need to be mention all about as Animation) from podcast transcription. Every time when i send a message,  your answer must being this format below with no need to change it. and if you didn't know in line just answer "-".

{"content" : 1 paragraph short message of a viewpoint or attitude summarization, but don't answer like "VFX, Game, Animation". these should be useful for cg artist.
"content_improve" : length of string target is 90. impovement/summarize and make more shorter as much as possible from "content" in a shortest paragraph (3-5 phrases and 12-20 words and 3 sentences).
"topic" : Target words count is 3-4. What is a topic from "content", give me that topic. and should be relate to work, animation, industry, pro tips, career. as a string format for this answer.
"topic_th" : Thai language translated utf-8 of "topic".
"content_th" : shortest massage Thai language translated utf-8 from "content_improve".
"credit" : If you found who are saying which you summaried, give their name but should be not main speaker. "Unknown" if you aren't sure.
"audience_tag" : tag of the audience saperate by department e.g. Animator, Producer, Pipeline, Rigger, Modeller, Etc. as a python list square bucket format for this answer.
"main_speaker" : If you found who are a main speaker. "Unknown" if you aren't sure.}

must be json string format and must be readable by using json.loads() in python.
        '''
        for i in range(3):
            system_prompt = system_prompt.replace('  ', ' ')

        self.openai.api_key = self.dc_cfg['open_ai_gpt']['api_key']
        try:
            completion = self.openai.ChatCompletion.create(
                model=self.dc_cfg['open_ai_gpt']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message + '\nreply me as json string format only'}
                ],
                temperature=0.25,
            )
            return completion
        except Exception as e:
            import traceback
            print(str(traceback.format_exc()))
            print('      GPT Completion error following all above ^      \n')
            time.sleep(5)
            return None
        '''
        Example completion
        {'choices': [{'finish_reason': 'stop',
                      'index': 0,
                      'message': {'content': '{"topic": "Career in Animation", \n'
                                             '"content": "In animation, it\'s '
                                             'important to create natural movement and '
                                             'avoid repetitive actions, such as '
                                             'characters always talking with the same '
                                             'gestures. Finding ways to innovate in '
                                             'animation leads to a successful '
                                             'career.", \n'
                                             '"credit": "Unknown", \n'
                                             '"main_speaker": "Unknown"}',
                                  'role': 'assistant'}}],
         'created': 1682613247,
         'id': 'chatcmpl-79yrH4oOjhwgc6qVehw2Dx5SbU0ia',
         'model': 'gpt-3.5-turbo-0301',
         'object': 'chat.completion',
         'usage': {'completion_tokens': 66,
                   'prompt_tokens': 281,
                   'total_tokens': 347}}
        '''

    def add_new_quote(self):
        transcript = self.get_rand_transcript_line()
        transcript['title2'] = transcript['title']
        #print(transcript)
        message = '''
Title : {0}
Massage : \"{1}\" '''.format(transcript['title2'], transcript['content'])

        # Notion init check
        title_key = transcript['file_name'].split('.')[0] + '_{:0>3d}'.format(transcript['line_number'])
        title_key = title_key.replace('__','_')
        transcript['title'] = title_key
        db_filter = {
            'property': 'title',
            'rich_text': {
                'contains': title_key
            }
        }
        db_data = notionDatabase.getDatabase(self.ntdb_id, filter=db_filter)
        if db_data['results'] != []:
            print('passed page exists [{}]'.format(db_data['results'][0]['id']))
            return None

        # Chat GPT
        completion = self.get_completion_response(message)
        if completion == None: return None
        try:
            gpt_content = json.loads(completion['choices'][0]['message']['content'])
        except Exception as e:
            import traceback
            print('\n============ GPT ERROR ===============')
            pprint.pprint(completion)
            print(str(traceback.format_exc()))
            gpt_content = completion['choices'][0]['message']['content']

        if type(gpt_content) == dict:
            # print(completion)
            print('\n============ READ GPT JSON STR ===============')
            pprint.pprint(gpt_content)
            if len(gpt_content['content_improve']) < len(gpt_content['content']):
                transcript['content'] = gpt_content['content_improve']
            else:
                transcript['content'] = gpt_content['content']
            transcript['credit'] = gpt_content['credit']
            transcript['topic'] = gpt_content['topic']
            transcript['content_th'] = gpt_content['content_th']
            transcript['topic_th'] = gpt_content['topic_th']
            transcript['main_speaker'] = gpt_content['main_speaker']
            transcript['audience_tag'] = random.sample(gpt_content['audience_tag'], len(gpt_content['audience_tag']))
            # transcript['topic'] = gpt_content['topic']
        elif type(gpt_content) == str:
            transcript['content'] = ''
            transcript['gpt_content'] = gpt_content

        # new page
        if db_data['results'] == []:
            page = notionDatabase.createPage(ntdb_id, 'title', title_key)
            properties = [i for i in list(page['properties'])]
            #print(properties)
            for col in transcript:
                if not col in properties:
                    del transcript[col]
            notionDatabase.update_page_properties(page['id'],transcript)
            '''
            for col in transcript:
                if col in properties:
                    #print([col], [transcript[col]], [transcript[col]])
                    notionDatabase.updatePageProperty(page['id'], col, transcript[col])
            '''
        else:
            page = db_data['results'][0]
        print('\n===========================\n')

    def get_random_quote_data(self):
        db_filter = {
              "property": "is_requested",
              "checkbox": {
                "equals": 'false'
              }
        }
        j_rec = notionDatabase.get_json_rec(self.ntdb_id, page_size=100, filter={})
        rand_idx = random.randint(0, len(j_rec)-1)
        data = j_rec[rand_idx]
        #pprint.pprint(data)
        notionDatabase.update_page_properties(data['page_id'], {'is_requested' : True})

        def separate_string(input_string, len_limit=40):
            words = input_string.split()
            lines, idx = ([''], 0)
            for i in range(len(words)):
                if len(lines[idx]) + len(words[i]) > len_limit:
                    idx += 1
                    lines.append('')
                lines[idx] = lines[idx] + ' ' + words[i]
            return lines

        for i in ['content']+['content_th']:
            data[i] = '\n'.join(separate_string(data[i]))
        return data

if __name__ == '__main__':

    qd = quote_daily()
    #qd.load_podcast_transcript()
    qd.get_random_quote_data()
    '''
    for i in range(1000):
        qd.get_rand_transcript_line()
        print(len(qd.text_path_cache))
    '''
    #print(qd.get_rand_transcript_line())

    '''
    while True:
        for i in range(15):
            qd.add_new_quote()
            #try: qd.add_new_quote()
            #except: pass
            #time.sleep(2)
        time.sleep(18)
    '''

    #base_path = os.sep.join(rootPath.split(os.sep)[:-1])

    #import system_manager
    #system_manager.integration.init_notion_db()
    #system_manager.integration.load_notion_db()
    #system_manager.integration.notion_sheet()

    #load_worksheet('AnimationTracking', base_path + '/production_rec')
    #finance.get_finance_doc_link()
    #finance.get_document_review()
    #finance.auto_generate_document()
    #print(project.get_member_workload('Ailynn AIS', 'Kaofang.B71'))
    #project.get_member_workload('Financial_test1', 'Kaofang.B71')

    #register.update_member()
    #task_queue.run(dev_mode=True)
    #project.update_invite()
    #project.add_member(346164580487004171, 'Project_Test', 20)
    pass

    #loadNotionDatabase(base_path + '/production_rec/notionDatabase')