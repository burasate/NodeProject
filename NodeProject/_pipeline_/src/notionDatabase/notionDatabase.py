import requests, json, pprint, os, random, csv
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', lambda x: '%.9f' % x)
pd.reset_option('display.float_format', silent=True)

#-------------------------------------
# Init
#-------------------------------------
config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.json'
with open(config_path) as config_f:
    config_j = json.load(config_f)
token = config_j['token']
database = config_j['database']
headers = {
        'Accept': 'application/json',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

"""-------------------------------------"""
# Func
"""-------------------------------------"""
def getDatabase(database_id, filter={}, page_size=5000):
    global headers
    url = 'https://api.notion.com/v1/databases/{}/query'.format(database_id)
    payload = {
        'page_size' : page_size
    }
    if filter != {}:
        payload['filter'] = filter
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    #pprint.pprint(response.json())
    return response.json()

def getPage(page_id):
    global headers
    url = 'https://api.notion.com/v1/pages/{}'.format(page_id)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    #pprint.pprint(response.json())
    return response.json()

def getPageProperty(page_id, property_id):
    global headers
    url = 'https://api.notion.com/v1/pages/{}/properties/{}'.format(page_id, property_id)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    #pprint.pprint(response.json())
    return response.json()

def createPage(database_id, title_name, name): #add row to database
    global headers
    url = 'https://api.notion.com/v1/pages'
    payload = {
        'parent' : {'database_id': database_id},
        'properties' : {
            title_name : [{
                'text' : {'content' : name}
            }]
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    res_j = response.json()
    #pprint.pprint(res_j)
    if res_j['object'] == 'error':
        raise Warning(res_j['message'])
    elif res_j['object'] == 'page':
        print('added new row to database {} : {}'.format(title_name, name))
        return res_j

def updatePage(database_id, find_name, delete = False, icon_emoji = '' , cover_link = ''): # delete / change icon, cover
    global headers
    database_data = getDatabase(database_id)
    #pprint.pprint(database_data)
    prop_dict = database_data['results'][0]['properties']
    title_prop = [
        i for i in list(prop_dict) if prop_dict[i]['id'] == 'title'
    ][0]
    database_data = getDatabase(
        database_id,
        filter = {
            'property' : title_prop,
            'rich_text' : { 'contains' : find_name }
        }
    )
    #pprint.pprint(database_data)
    page_id = ''
    for row in database_data['results']:
        page_id = row['id'].replace('-','')
        page_data = getPageProperty(page_id, 'title')
        title_name = page_data['results'][0]['title']['plain_text']
        #pprint.pprint(title_name)
        #print('find ', title_name, page_id, title_name == find_name)
        if find_name != title_name:
            page_id = ''
            continue
        else:
            break
    if page_id == '':
        return None

    url = 'https://api.notion.com/v1/pages/{}'.format(page_id)
    payload = {
        'archived' : delete
    }
    if icon_emoji != '':
        payload['icon'] = {
            'type': 'emoji',
            'emoji': icon_emoji
        }
    if cover_link != '':
        payload['cover'] = {
            'type' : 'external',
            'external': {'url': cover_link}
        }
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    res_j = response.json()
    if res_j['object'] == 'error':
        raise Warning(res_j['message'])
    elif res_j['object'] == 'page':
        print('update page / row  {}   {}'.format(page_id,payload))
        return res_j

def updatePageProperty(page_id, property, value):
    """
    :param page_id: row id in notion database
    :param property: column in notion database
    :param v_type: type of value/column
    :param value: any valu have relation of type
    :return: update notion database
    """
    page_data = getPage(page_id)
    if not property in page_data['properties']:
        raise Warning('property \'{}\' was not found in page'.format(property))

    prop_data = getPageProperty(page_id, page_data['properties'][property]['id'])
    #pprint.pprint(prop_data)
    v_type = None
    if 'property_item' in prop_data:
        v_type = prop_data['property_item']['type']
    else :
        v_type = prop_data['type']

    #print('found ', v_type)
    type_dict = {
        'title' : [{ # 'title'
            'type' : 'text',
            'text' : {'content' : str(value)}
        }],
        'rich_text' : [{ # 'some text'
            'type' : 'text',
            'text' : {'content' : str(value)}
        }],
        'select' : { # 'some text'
            'select' : {'name': str(value)}
        },
        'date' : { # '2010-01-01'
                'date': {
                    'start': str(value),
                    'end': None, 'time_zone': None,
                },
                'type': 'date'
        },
        'number': value,  # 1
        'email' : str(value),
        'phone_number' : str(value),
        'url' : str(value),
        'checkbox' : bool(value),
        'relation': [ # 'relation page id'
            {'id': str(value)}
        ],
        'multi_select': [  # 'select name'
            {'name': str(value)}
        ],
        'status' : {'name': str(value)},
    }

    if not v_type in type_dict:
        print('type ', list(type_dict))
        raise Warning('type \'{}\' was not found in dict\nso can\'t update to this property type.'.format(v_type))

    value_is_list = (type(value) == type(list()))
    if value_is_list:
        print('input value is list type..')
        if v_type == 'relation':
            type_dict[v_type] = [ {'id':i} for i in value ]
        if v_type == 'multi_select':
            type_dict[v_type] = [ {'name':i} for i in value ]

    global headers
    url = 'https://api.notion.com/v1/pages/{}'.format(page_id)
    payload = {
        'properties':
            {
                property : type_dict[v_type]
             },
        'archived': False
    }
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    res_j = response.json()
    #pprint.pprint(res_j)
    if res_j['object'] == 'error':
        print ('status', res_j['status'], 'https://developers.notion.com/reference/errors')
        raise Warning(res_j['message'])
    elif res_j['object'] == 'page':
        prop_id = res_j['properties'][property]['id']
        print('property ({}) \'{}\' : {}  updated'.format(prop_id, property, value))
        return res_j

def update_page_properties(page_id, properties_dict):
    """
    :param page_id: row id in notion database
    :param properties:
        properties_dict = {
            "Title": "New Title",
            "Description": "New Description",
            "Category": {"select": {"name": "New Category",
            "Priority": 3,
            "Status": ["New Status"}]
        }
        new_properties = {
            "Title": {"title": [{"text": {"content": "New Title"}}]},
            "Description": {"rich_text": [{"text": {"content": "New Description"}}]},
            "Category": {"select": {"name": "New Category"}},
            "Priority": {"number": 3},
            "Status": {"multi_select": [{"name": "New Status"}]}
        }
    :return: update notion database
    """
    page_data = getPage(page_id)
    for p in list(properties_dict):
        if not p in page_data['properties']:
            raise Warning('property \'{}\' was not found in page'.format(p))
    #pprint.pprint(page_data)

    v_type_dict = {}
    for p in list(properties_dict):
        prop_data = page_data['properties'][p]
        #pprint.pprint(prop_data)

        v_type = None
        if 'property_item' in prop_data:
            v_type = prop_data['property_item']['type']
        else :
            v_type = prop_data['type']
        v_type_dict[p] = v_type
    #pprint.pprint(v_type_dict)

    new_properties = {}
    for p in list(properties_dict):
        value = properties_dict[p]
        v_type = v_type_dict[p]

        type_dict = {
            'title' : [{ # 'title'
                'type' : 'text',
                'text' : {'content' : str(value)}
            }],
            'rich_text' : [{ # 'some text'
                'type' : 'text',
                'text' : {'content' : str(value)}
            }],
            'select' : { # 'some text'
                'select' : {'name': str(value)}
            },
            'date' : { # '2010-01-01'
                    'date': {
                        'start': str(value),
                        'end': None, 'time_zone': None,
                    },
                    'type': 'date'
            },
            'number': value,  # 1
            'email' : str(value),
            'phone_number' : str(value),
            'url' : str(value),
            'checkbox' : bool(value),
            'relation': [ # 'relation page id'
                {'id': str(value)}
            ],
            'multi_select': [  # 'select name'
                {'name': str(value)}
            ],
            'status' : {'name': str(value)},
        }

        if not v_type in type_dict:
            print('type ', list(type_dict))
            raise Warning('type \'{}\' was not found in dict\nso can\'t update to this property type.'.format(v_type))

        value_is_list = (type(value) == type(list()))
        if value_is_list:
            print('input value is list type..')
            if v_type == 'relation':
                type_dict[v_type] = [{'id': i} for i in value]
            if v_type == 'multi_select':
                type_dict[v_type] = [{'name': i} for i in value]

        new_properties[p] = type_dict[v_type]

    #pprint.pprint(new_properties)

    global headers
    url = 'https://api.notion.com/v1/pages/{}'.format(page_id)
    payload = {
        'properties': new_properties,
        'archived': False
    }
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    res_j = response.json()
    #pprint.pprint(res_j)
    if res_j['object'] == 'error':
        print ('status', res_j['status'], 'https://developers.notion.com/reference/errors')
        raise Warning(res_j['message'])
    elif res_j['object'] == 'page':
        prop_id = res_j['properties'][p]['id']
        print('properties ({})  : {}  updated'.format(prop_id, properties_dict))
        return res_j

def del_page_id(page_id):
    global headers
    url = 'https://api.notion.com/v1/pages/{}'.format(page_id)
    payload = {
        'archived': True
    }
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
    print('deleted/archived  : {}'.format(page_id))
    # pprint.pprint(response.json())
    #return response.json()

#version 1
def notionJsonParser(database_id, dir_path, replace_name = '', force_update = False):
    j_path = dir_path + '/' + database_id + '.json'
    if replace_name != '':
        j_path = dir_path + '/' + replace_name + '.json'
    print(j_path)

    data = {}

    # Force Update
    if force_update:
        try:
            os.remove(j_path)
        except:
            pass

    # Load Exist
    if os.path.exists(dir_path) and os.path.exists(j_path):
        try :
            with open(j_path, 'r') as f:
                data = json.load(f)
                #pprint.pprint(list(data))
        except :
            os.remove(j_path)

    # Load Update
    db = getDatabase(database_id)
    if db['object'] == 'error':
        if db['code'] == 'object_not_found':
            if os.path.exists(j_path):
                os.remove(j_path)
            return None
        else:
            raise Warning(db)

    page_id_list = [db['results'][i]['id'].replace('-','') for i in range(len(db['results']))]
    data_id_list = [i for i in data]
    data_id_del_list = [i for i in data_id_list if not i in page_id_list]
    for i in data_id_del_list:
        print('Delete {}'.format(i))
        del data[i]
        with open(j_path, 'w') as f:
            json.dump(data, f, indent=4)

    for row in db['results']:
        index = db['results'].index(row)
        last_edited_time = ''.join([
            s for s in row['last_edited_time'].replace('T', ' ') if s in [' ', '-', ':', '.'] or s.isdigit()
        ]).split('.')[0]
        page_id = row['id'].replace('-','')
        prop_list = [i for i in row['properties']]
        try:
            title = getPageProperty(page_id, 'title')
        except:
            continue

        if title['results'] != []:
            title = title['results'][0]['title']['plain_text']
        else:
            title = ''
        # print(key_list)
        # print(page_id)
        # print(row['object'])

        print('Row ', '{} columns'.format(len(prop_list)), title),
        if (
            page_id in data and
            data[page_id]['last_edited_time'] == last_edited_time and
            sorted(prop_list) == sorted(data[page_id]['properties'])
        ):
            continue
        prop_dict = {}
        for prop_name in prop_list:
            item = getPageProperty(page_id, row['properties'][prop_name]['id'])
            typ = item['type']
            obj = item['object']
            value = None
            print(prop_name, '---->', (obj,typ), str(item)[:60])
            if obj == 'list' and typ == 'property_item':
                if item['results'] != [] and item['property_item']:
                    paser_list = []
                    for i in item['results']:
                        #pprint.pprint(i)
                        if 'relation' in i:
                            relation_id = i['relation']['id'].replace('-','')
                            relation_data = getPageProperty(relation_id, 'title')
                            plain_text = relation_data['results'][0]['title']['plain_text']
                            paser_list.append(plain_text)
                        elif 'rich_text' in i:
                            plain_text = i['rich_text']['plain_text']
                            paser_list.append(plain_text)
                        elif 'title' in i:
                            plain_text = i['title']['plain_text']
                            paser_list.append(plain_text)
                        elif 'number' in i:
                            number = i['number']
                            paser_list.append(str(number))
                        elif 'multi_select' in i:
                            name_list = ','.join([i['name'] for i in i['multi_select']])
                            paser_list.append(name_list)
                        else : pass
                            #1/0
                    value = ','.join(paser_list)
                else:
                    if 'rollup' in item['property_item']:
                        print('found rollup - parser unsupported')
                    value = None

                if 'rollup' in item['property_item'] and 'number' in item['property_item']['rollup']:
                    value = item['property_item']['rollup']['number']

            elif obj == 'property_item' and typ == 'date':
                if item[typ] != None:
                    if item[typ]['start'] != None and item[typ]['end'] != None:
                        value = ','.join([ item[typ]['start'], item[typ]['end'] ])
                    elif item[typ]['start'] != None and item[typ]['end'] == None:
                        value = ','.join([item[typ]['start']])
                    else:
                        value = ''
                else:
                    value = None

            elif obj == 'property_item' and typ == 'url':
                value = item[typ]

            elif obj == 'property_item' and typ == 'multi_select':
                if item['multi_select'] != []:
                    paser_list = []
                    for i in item['multi_select']:
                        plain_text = i['name']
                        paser_list.append(plain_text)
                    value = ','.join(paser_list)

            elif obj == 'property_item' and typ == 'created_time':
                value = ''.join([
                    s for s in item[typ].replace('T', ' ') if s in [' ', '-', ':', '.'] or s.isdigit()
                ]).split('.')[0]

            elif obj == 'property_item' and typ == 'formula':
                value = item[typ][item[typ]['type']]

            elif obj == 'property_item' and typ == 'number':
                value = item[typ]

            elif obj == 'property_item' and typ == 'email':
                value = item[typ]

            elif obj == 'property_item' and typ == 'status':
                if item[typ] != None:
                    value = item[typ]['name']
                else:
                    value = None

            elif obj == 'property_item' and typ == 'created_by':
                if item[typ] != None:
                    value = item[typ]['name']
                else:
                    value = None

            elif obj == 'property_item' and typ == 'select':
                if item[typ] != None:
                    value = item[typ]['name']
                else:
                    value = None
            elif obj == 'property_item' and typ == 'checkbox':
                value = bool(item['checkbox'])

            else: pass
                #1/0
            print(value, '\n')
            #db['results'][index]['properties'][prop_name] = value
            prop_dict[prop_name] = value

        data[page_id] = {}
        data[page_id]['title'] = title
        data[page_id]['page_id'] = page_id
        data[page_id]['last_edited_time'] = ''.join([
            s for s in db['results'][index]['last_edited_time'].replace('T', ' ') if s in [' ', '-', ':', '.'] or s.isdigit()
        ]).split('.')[0]
        data[page_id]['properties'] = prop_dict

    with open(j_path, 'w') as f:
        json.dump(data, f, indent=4)
#version 2
def json_parser(database_id, dir_path, replace_name = ''):
    j_path = dir_path + '/' + database_id + '.json'
    if replace_name != '':
        j_path = dir_path + '/' + replace_name + '.json'
    print(j_path)
    rec = get_json_rec(database_id, page_size=5000)
    with open(j_path, 'w') as f:
        json.dump(rec, f, indent=4)

def get_json_rec(database_id, page_size=100, filter={}):
    print(database_id)
    def get_page_record(data):
        ls_mrk, tp_mrk = ['$list', '$type']
        type_dict = {
            'multi_select': ['multi_select', ls_mrk, 'name'],
            'checkbox': ['checkbox'],
            'rich_text': ['rich_text', ls_mrk, 'text', 'content'],
            'select': ['select'],
            'created_time': ['created_time'],
            'status': ['status', 'name'],
            'formula': ['formula', tp_mrk],
            'number': ['number'],
            'title': ['title', ls_mrk, 'text', 'content'],
            'relation': ['relation', ls_mrk, 'id'],
            'rollup': ['rollup', tp_mrk],
            'url': ['url'],
            'email': ['email'],
            'date': ['date'],
            'created_by': ['created_by'],
            'last_edited_time': ['last_edited_time'],
        }

        properties = list(data['results'][0]['properties'])
        #print(properties)
        records = []
        for item in data['results']:
            rec_data = {
                'title' : '',
                'page_id' : item['id'],
                'last_edited_time' : item['last_edited_time'],
                'created_time' : item['created_time'],
            }
            for prop in properties:
                result = item['properties'][prop]
                type = item['properties'][prop]['type']
                sub_ls = []
                #print('\n{}'.format(result))
                for path in type_dict[type]:
                    if path == tp_mrk:
                        sub_type = result['type']
                        result = result[sub_type]
                        #print(result)
                        break
                    if path == ls_mrk:
                        idx = type_dict[type].index(path)
                        sub_ls = type_dict[type][idx+1:]
                        #print(sub_ls)
                        continue
                    elif sub_ls != []:
                        for sub_path in sub_ls:
                            result = [i[sub_path] for i in result]
                        result = ', '.join(result)
                        #print(result)
                        break
                    else:
                        result = result[path]
                        #print(result)
                #print([result])
                if type == 'title':
                    rec_data['title'] = result
                rec_data[prop] = result
            #append data
            records.append(rec_data)
        #print(records)
        return records

    page_size_remain = page_size
    payload = {
        'page_size': page_size,
    }
    if filter != {}:
        payload['filter'] = filter
    url = 'https://api.notion.com/v1/databases/{}/query'.format(database_id)

    all_rec = []
    while page_size_remain > 0:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Warning('Internet connection issue or get error response\n{}'.format(response.text))
        data = response.json()
        all_rec += get_page_record(data)

        page_size_remain -= len(data['results'])
        if not data['has_more']:
            break
        elif data['has_more']:
            payload['start_cursor'] = data['next_cursor']

    #os.system('cls||clear')
    #pprint.pprint(all_rec[0])
    print(len(all_rec), database_id)
    return all_rec

def loadNotionDatabase(dir_part):
    global database
    random.shuffle(database)

    for i in database:
        os.system('cls||clear')
        json_parser(i['id'], dir_part, replace_name=i['name'])

        #json to csv
        j_part = dir_part + '/{}.json'.format(i['name'])

        if not os.path.exists(j_part):
            continue

        with open(dir_part + '/{}.json'.format(i['name'])) as data_f:
            data_j = json.load(data_f)
        csv_dir = dir_part + '/csv'
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        csv_path = csv_dir + '/{}.csv'.format(i['name'])
        if os.path.exists(csv_path):
            try:
                os.remove(csv_path)
            except:
                pass

        df = pd.DataFrame().from_records(data_j)
        if df.empty:
            raise Warning('the database need to add some page for works')
        '''
        for row_id in data_j:
            properties = data_j[row_id]['properties']
            data = {
                'page_id': row_id,
                'title': data_j[row_id]['title'],
                'last_edited_time': data_j[row_id]['last_edited_time']
            }
            for prop_name in properties:
                data[prop_name] = properties[prop_name]
            df = df.append(pd.DataFrame.from_records([data]))

        if df.empty:
            raise Warning('the database need to add some page for works')
        '''
        df = df[['page_id', 'title'] + sorted([
            i for i in df.columns.tolist() if not i in ['page_id', 'title']], reverse=False)]
        df.reset_index(inplace=True, drop=True)
        df = df.convert_dtypes('str')
        df.dropna(subset=['title'], inplace=True)
        df.to_csv(csv_path, index=False, encoding='utf-8')

if __name__ == '__main__':
    #pprint.pprint(getDatabase('6ed27678-c64b-46fa-bd8c-5a398c9aff57'))
    #pprint.pprint(getPage('ccada1eb75724048a37442ab778e5d33'))
    #pprint.pprint(getPageProperty('ccada1eb75724048a37442ab778e5d33','rx%3B%7D'))
    #pprint.pprint(getPageProperty('dfcd88e1-f007-4d18-80ec-5c4280dd16e5', 'title')) #Reation
    #updatePageProperty('4c4aa72787e6487ca8bd7e01be74219b', 'team', ['dee9719d0bb64084ba84c06692c45031'])
    #updatePageProperty('4c4aa72787e6487ca8bd7e01be74219b', 'Invite', 0)
    #createPage('bc5ca11036ff4da9b723b250ad658807','project_name', 'new')
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name', delete=True)  #do delete
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name') #do nothing
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name', icon_emoji='🎉') #change icon
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name', cover_link='http://') #change cover
    #update_page_properties('1c98c4f6d31a409a9c90280f47daac73',{'first_name' : 'Burased','last_name' : 'Uttha','hour_per_week' : 20,})
    #get_json_rec('c29a633124b94bfc88633f6da1f9ba71')
    #get_json_rec('6f7393d8cb6445b0b9908036637626c6')
    #json_parser('c29a633124b94bfc88633f6da1f9ba71', r'C:\Users\DEX3D_I7\Desktop\Periodic Autoencoder Code', 'all_data')
    pass