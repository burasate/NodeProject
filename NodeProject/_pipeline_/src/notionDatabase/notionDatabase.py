import requests, json, pprint, os, random, csv
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

#-------------------------------------
# Init
#-------------------------------------
with open(os.path.dirname(os.path.abspath(__file__)) + '/config.json') as config_f:
    config_j = json.load(config_f)
token = config_j['token']
database = config_j['database']
headers = {
        'Accept': 'application/json',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

#-------------------------------------
# Func
#-------------------------------------
def getDatabase(database_id, filter={}):
    global headers
    url = 'https://api.notion.com/v1/databases/{}/query'.format(database_id)
    payload = {
        'page_size' : 25
    }
    if filter != {}:
        payload['filter'] = filter
    response = requests.post(url, json=payload, headers=headers)
    #pprint.pprint(response.json())
    return response.json()

def getPage(page_id):
    global headers
    url = 'https://api.notion.com/v1/pages/{}'.format(page_id)
    response = requests.get(url, headers=headers)
    #pprint.pprint(response.json())
    return response.json()

def getPageProperty(page_id, property_id):
    global headers
    url = 'https://api.notion.com/v1/pages/{}/properties/{}'.format(page_id, property_id)
    response = requests.get(url, headers=headers)
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

    print('found ', v_type)
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
    res_j = response.json()
    #pprint.pprint(res_j)
    if res_j['object'] == 'error':
        print ('status', res_j['status'], 'https://developers.notion.com/reference/errors')
        raise Warning(res_j['message'])
    elif res_j['object'] == 'page':
        prop_id = res_j['properties'][property]['id']
        print('property ({}) \'{}\' : {}  updated'.format(prop_id, property, value))
        return res_j

def notionJsonParser(database_id, dir_path, replace_name = ''):
    j_path = dir_path + '/' + database_id + '.json'
    if replace_name != '':
        j_path = dir_path + '/' + replace_name + '.json'
    print(j_path)

    data = {}
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
        title = getPageProperty(page_id, 'title')
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
                    value = ','.join([ item[typ]['start'], item[typ]['end'] ])
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

def loadNotionDatabase(dir_part):
    global database
    random.shuffle(database)

    for i in database:
        os.system('cls||clear')
        notionJsonParser(i['id'], dir_part, replace_name=i['name'])

        #json to csv
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

        df = pd.DataFrame()
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
        if not df.empty:
            df = df[['page_id', 'title', 'last_edited_time'] + sorted(list(properties), reverse=False)]
            df.reset_index(inplace=True, drop=True)
        df.to_csv(csv_path, index=False)
        
if __name__ == '__main__':
    #pprint.pprint(getPage('4c4aa72787e6487ca8bd7e01be74219b'))
    #pprint.pprint(getPageProperty('4c4aa72787e6487ca8bd7e01be74219b','rx%3B%7D'))
    #pprint.pprint(getPageProperty('6fc9e25c-7f93-4013-851a-214a27287714', 'title')) #Reation
    #updatePageProperty('4c4aa72787e6487ca8bd7e01be74219b', 'team', ['dee9719d0bb64084ba84c06692c45031'])
    #updatePageProperty('4c4aa72787e6487ca8bd7e01be74219b', 'Invite', 0)
    #createPage('bc5ca11036ff4da9b723b250ad658807','project_name', 'new')
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name', delete=True)  #do delete
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name') #do nothing
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name', icon_emoji='🎉') #change icon
    #updatePage('bc5ca11036ff4da9b723b250ad658807', 'row title name', cover_link='http://') #change cover
    pass