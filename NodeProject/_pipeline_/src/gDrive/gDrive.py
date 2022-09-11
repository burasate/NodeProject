from Google import Create_Service
import pprint
import pandas as pd

#Reference
#https://developers.google.com/drive/api/v3/reference/files

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def get_files(folder_id):
    data = get_metadata(folder_id)
    if data['mimeType'] != 'application/vnd.google-apps.folder':
        print('request folder id')
        return None
    query = 'parents = \'{}\''.format(folder_id)
    r = service.files().list(q=query).execute()
    files = r.get('files')
    nextPageToken = r.get('nextPageToken')

    while nextPageToken:
        r = service.files().list(q=query).execute()
        files.extend(r.get('files'))
        nextPageToken = r.get('nextPageToken')

    #pprint.pprint(files)
    return files

def create_folder(parent_id, folder_name):
    items = get_files(parent_id)
    folder_list = [i['name'] for i in items if 'google-apps.folder' in i['mimeType']]
    if not folder_name in folder_list:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        service.files().create(body=file_metadata).execute()
        print('create folder \"{}\" in folder id {} finish'.format(folder_name, parent_id))
    else:
        print('\"{}\" exists the skipped'.format(folder_name))

def get_metadata(item_id):
    data = service.files().get(fileId=item_id, fields='*').execute()
    return data

def move(item_id, target_folder_id):
    data = get_metadata(item_id)
    source_folder_id = data['parents'][0]
    service.files().update(
        fileId=item_id,
        addParents=target_folder_id,
        removeParents=source_folder_id
    ).execute()

def delete(item_id):
    service.files().delete(fileId=item_id).execute()

def create_share_anyone(item_id):
    request_body = {
        'role' : 'reader',
        'type' : 'anyone'
    }
    r = service.permissions().create(
        fileId=item_id,
        body=request_body
    ).execute()
    #pprint.pprint(r)
    data = get_metadata(item_id)
    #print(data['webViewLink'])
    return data['webViewLink']

def romove_share_anyone(item_id):
    service.permissions().delete(
        fileId=item_id,
        permissionId='anyoneWithLink'
    ).execute()

def create_share_email(item_id, email):
    request_body = {
        'role': 'reader',
        'type': 'user',
        'emailAddress' : email
    }
    r = service.permissions().create(
        fileId=item_id,
        body=request_body
    ).execute()
    pprint.pprint(r)

def remove_share_email(item_id, email):
    permission_list = service.permissions().list(
        fileId=item_id,
        fields='*'
    ).execute()['permissions']
    #pprint.pprint(permission_list)
    email_list = [i for i in permission_list if i['emailAddress'] == email]
    if email_list == []:
        return None
    email_sl = email_list[0]
    service.permissions().delete(
        fileId=item_id,
        permissionId=email_sl['id']
    ).execute()


if __name__ == '__main__':
    pprint.pprint(get_files('1ytUrK5iVPlBjtel08VA1RMaCW0N-b04_'))

    #x = ['a', 'd']
    #for i in x:
        #create_folder('1ytUrK5iVPlBjtel08VA1RMaCW0N-b04_', i)

    #pprint.pprint(get_metadata('1QOLU2uLWc_b_RPsYyJfVxHMxbt-rrIgK'))

    #move(item_id = '1A3c16f2-fC25HBMffADs1bgBdAl4j_BC',
         #target_folder_id = '1odseDCKkg78nTVA0ozM9RolPV0eMlmx1')

    #delete('1A3c16f2-fC25HBMffADs1bgBdAl4j_BC')

    #create_share_anyone('1A6z0QAJUPi6mHu_T9danfe7j7bnQVQsv')
    #romove_share_anyone('1A6z0QAJUPi6mHu_T9danfe7j7bnQVQsv')

    #create_share_email('1A6z0QAJUPi6mHu_T9danfe7j7bnQVQsv', 'kanlayamart5437@gmail.com')
    remove_share_email('1A6z0QAJUPi6mHu_T9danfe7j7bnQVQsv', 'kanlayamart5437@gmail.com')
    pass
