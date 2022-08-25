import requests, os

base_path = os.path.dirname(os.path.abspath(__file__))
update_txt = base_path + '/raspi_update.txt'

def update(*_):
    f_read = open(update_txt)
    update_list = f_read.readlines()

    update_list_url = 'https://raw.githubusercontent.com/burasate/NodeProject/main/NodeProject/_pipeline_/raspi_update.txt'
    update_list_r = requests.get(update_list_url)
    if update_list_r.status_code == 200:
        update_list = update_list_r.text.split('\n')
    print('Loading Update List')
    print(update_list)

    for url in update_list:
        os.system('cls||clear')
        if not 'https://' in url:
            continue

        url = url.replace('\n','').replace('\\','/')
        url_split = url.split('/')
        base_dir_name = base_path.split(os.sep)[-1]
        dest_path = base_path.replace('\\','/') + '/' + '/'.join(url_split[(url_split.index(base_dir_name))+1:])

        print(url)
        #rint(dest_path)
        r = requests.get(url)
        status_code = r.status_code
        # print(r.text)
        #print(status_code, status_code == 200)

        print('updating ' + dest_path.split('/')[-1])
        #NT Danger Zone
        if not os.name == 'nt' and status_code == 200:
            try:
                dest_file = open(dest_path, 'w')
                dest_file.writelines(r.text)
                dest_file.close()
                print('update {} success'.format(dest_path.split('/')[-1]))
            except Exception as e:
                import traceback
                print(str(traceback.format_exc()))
                print('update {} fail'.format(dest_path.split('/')[-1]))
        else:
            print('     skiped for os nt')

if __name__ == '__main__':
    update()

if __name__ == 'raspi_update' and not os.name == 'nt':
    update()