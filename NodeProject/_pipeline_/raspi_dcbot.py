# -*- coding: utf-8 -*-
import os, csv, os, json, time, pprint, sys, shutil, random
"""
https://discordpy.readthedocs.io/en/stable/api.html
https://autocode.com/tools/discord/embed-builder/
"""
"""---------------------------------"""
# Init
"""---------------------------------"""
base_path = os.path.dirname(os.path.abspath(__file__))
#print(base_path)
src_path = base_path+'/src'
print(sys.version)

package_dir_ls = [base_path, src_path]
if sys.version.split('.')[1] == '10':
    package_dir_ls += [src_path + os.sep + 'site-packages_3.10']
for p in package_dir_ls:
    if not p in sys.path:
        #print('init package dir     {}'.format(p))
        sys.path.insert(1,p)
print(sorted(sys.builtin_module_names))
print(json.dumps([i.replace('\\','/') for i in sys.path], indent=4))

from discord.ext import commands, tasks
import urllib, asyncio, discord, requests
import datetime as dt
import pandas as pd
import numpy as np
import urllib.parse

from notionDatabase import notionDatabase as ntdb
from gSheet import gSheet
gSheet.sheetName = 'Node Project Integration'
import system_manager
import production_manager

config_file_name = os.path.basename(os.path.abspath(__file__)).replace('.py','.json')
with open(base_path + '/' + config_file_name) as config_f:
    config_j = json.load(config_f)
token = config_j['token']
sever_id = config_j['sever_id']

intents = discord.Intents.all()
intents.members = True
intents.messages = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
if os.name == 'nt':
    bot = commands.Bot(command_prefix='/', intents=intents)

channel_dict = {
    'log' : 1011320896063021147,
    'member_welcome' : 1012248546050846720,
    'welcome' : 920741438516523051,
    'report' : 1012257225726771281
}

class bot_func:
    @staticmethod
    def add_queue_task(task_name, data_dict):
        if type(data_dict) != type(dict()):
            return None
        data = {
            'name': task_name,
            'data': data_dict
        }
        data['data'] = json.dumps(data['data'], indent=4, sort_keys=True)
        url = 'https://script.google.com/macros/s/AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJjj2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec'
        response = requests.post(url, params=data)
        print(response.text)
        print(data)

    @staticmethod
    def get_ctx_data(ctx):
        data = {
            'guild': {
                'id': ctx.guild.id,
                'name': ctx.guild.name,
                'member_count': ctx.guild.member_count,
                'roles': []
            },
            'message': {
                'content': ctx.message.content,
                'id': ctx.message.id
            },
            'category': {},
            'channel': {
                'id': ctx.channel.id,
                'name': ctx.channel.name
            },
            'author': {
                'id': ctx.author.id,
                'name': ctx.author.name,
                'mention' : ctx.author.mention,
                'bot': ctx.author.bot,
                'nick': ctx.author.nick,
                'roles': []
            }
        }
        for i in ctx.guild.roles:
            data['guild']['roles'].append({
                'id': i.id,
                'name': i.name,
                'mention': i.mention,
            })
        for i in ctx.author.roles:
            data['author']['roles'].append({
                'id': i.id,
                'name': i.name})
        if ctx.channel.category != None:
            data['category']['name'] = ctx.channel.category.name
            data['category']['id'] = ctx.channel.category.id

        return data

    def get_guild():
        guild = [bot.guilds[i] for i in range(len(bot.guilds)) if str(bot.guilds[i].id) == sever_id][0]
        return guild

    @staticmethod
    def get_notino_db(csv_name, dropna=False):
        prev_dir = os.sep.join(base_path.split(os.sep)[:-1])
        file_path = prev_dir + '/production_rec/notionDatabase/csv/{}.csv'.format(csv_name)

        df = pd.read_csv(file_path, dtype='str')
        if dropna:
            df.dropna(subset=['title'],inplace=True)
        rec = []
        for i in df.index.tolist():
            row = df.loc[i]
            rec.append(row.to_dict())
        return rec

    @staticmethod
    def get_translate(msg_content, target_lang):
        print(f'translate into {target_lang}...')
        data = gSheet.getAllDataS('dc_translate')
        row_name_list = [i['row_name'] for i in data]
        if data[row_name_list.index('target_source')]['target_language'] != target_lang:
            gSheet.setValue('dc_translate', findKey='row_name', findValue='target_source', key='target_language',value=target_lang)
        if data[row_name_list.index('input_output')]['source_language'] != msg_content:
            gSheet.setValue('dc_translate', findKey='row_name', findValue='input_output', key='source_language',
                            value=msg_content)

        time.sleep(3)
        data_new = gSheet.getAllDataS('dc_translate')
        result = data_new[row_name_list.index('input_output')]['target_language']
        #print(result)
        return result

"""---------------------------------"""
# Discord Start
"""---------------------------------"""
@bot.event
async def on_ready():
    print('========================')
    print('Discord ver {}\nPython ver {}'.format(discord.__version__, sys.version.split(' ')[0]))
    print('Bot : Online')
    print('========================')

    if not os.name == 'nt': # Rassberry pi
        #project_invite.start()
        print_time.start()
        on_running_status.start()
        vote_report.start()
        role_update.start()
        project_channel_update.start()
        #traceback_nortify.start()
        #auto_translate.start()
        dm_finance_document.start()
        dm_finance_review.start()
        auto_clear_all_dm_message.start()
        members_stat_record.start()
        members_stat_report.start()
    else:
        on_running_status.start()

"""---------------------------------"""
# Discord Sync
"""---------------------------------"""
@tasks.loop(minutes=30)
async def print_time():
    print(f'\n==========[     {dt.datetime.now()}     ]==========\n')

@tasks.loop(minutes=60)
async def on_running_status():
    channel = bot.get_channel(channel_dict['log'])

    messages = [i async for i in channel.history(limit=300) if i.author.bot]
    user_messages = [i async for i in channel.history(limit=300) if not i.author.bot]
    for message in messages: # clear history
        if 'Node running status' in message.content:
            await message.delete()
    for message in user_messages: # clear user message
        await message.delete()

    msg = '''
**{0}**
`Node was running at {1}

OS : {2}
Python Ver : {3}
Discord Ver : {4}`
'''.format('Node running status', dt.datetime.now().__str__(), os.name, sys.version, discord.__version__)
    await channel.send(msg)

@tasks.loop(minutes=10)
async def role_update():
    regis_rec = bot_func.get_notino_db('member', dropna=True)
    regis_id_list = [ i['discord_id'] for i in regis_rec if str(i['discord_id']).isdigit()]
    regis_id_list = [ int(i) for i in regis_id_list ]
    find_role_name = 'Node Freelancer'

    guild = bot_func.get_guild()
    member_id_list = [i.id for i in guild.members]
    apply_role = [i for i in guild.roles if find_role_name in i.name][0]

    channel = bot.get_channel(channel_dict['member_welcome'])
    messages = [message async for message in channel.history(limit=100) if bot.user.name == message.author.name]
    content_list = [i.clean_content for i in messages]

    for member in guild.members:
        member_id = int(member.id)
        member_roles = [i.name for i in member.roles]
        is_role_found = True in [ find_role_name in i for i in member_roles ]
        is_id_found = member_id in regis_id_list
        #'''
        #print(member.display_name , member_id, is_id_found) #show all member sync
        #'''
        if is_id_found:
            member_sl = [i for i in regis_rec if int(i['discord_id']) == member_id][0]
            user_name = member_sl['title']
            if not is_role_found:
                await member.add_roles(apply_role)
                try:await member.edit(nick=user_name)
                except:print('canot change nickname')

                msg = f'added {user_name} ({member.display_name}) to \"{apply_role.name}\" role'
                if not msg in content_list:
                    await channel.send(f'{msg}')
            if member.nick != user_name:
                await member.edit(nick=user_name)

        elif not is_id_found and is_role_found:
            await member.remove_roles(apply_role)

    print('member role updated')

@tasks.loop(minutes=5)
async def project_channel_update():
    guild = bot_func.get_guild()
    categories = guild.categories
    project_category = [i for i in categories if 'node' in (i.name).lower() and 'project' in (i.name).lower()][0]
    projects = bot_func.get_notino_db('project')
    project_name_list = [i['title'] for i in projects]
    project_id_list = [i['page_id'] for i in projects]
    channel_id_list = [str(i['discord_channel_id']) for i in projects]
    category_channel_list = [i.name for i in project_category.channels]
    category_channel_id_list = [int(i.id) for i in project_category.channels]
    prefix_ready, prefix_archive, prefix_voice = ['🟢proj-', '🔴proj-', '🎧proj-']

    # Exist
    for name in project_name_list :
        index = project_name_list.index(name)
        channel_name = ''.join([i for i in name if i.isalpha() or i.isspace() or i.isnumeric()])
        channel_name = channel_name.lower().strip()
        channel_name = channel_name.replace('-',' ').replace('_',' ').replace(' ','_')
        channel_name = prefix_ready + channel_name

        channel_id = str(channel_id_list[index])
        if not channel_id.isnumeric():
            channel_id = None
        else :
            channel_id = int(channel_id)

        is_name_exists = channel_name in category_channel_list
        is_id_exists =  False
        if channel_id != None:
            is_id_exists = channel_id in category_channel_id_list

        #print(channel_name, channel_id, is_name_exists, is_id_exists) #for check
        if not is_name_exists and not is_id_exists: #new
            channel = await guild.create_text_channel(channel_name)
            await channel.edit(category=project_category, sync_permissions=True)

            task_name = 'set_project_channel_id'
            task_data = {
                'channel_id' : channel.id,
                'project_name' : name,
                'project_id' : project_id_list[index]
            }
            bot_func.add_queue_task(task_name, task_data)
            print('Create project channel {}'.format(channel_name))

        elif is_id_exists and not is_name_exists: #rename
            find_index = category_channel_id_list.index(channel_id)
            find_name = category_channel_list[find_index]
            channel = bot.get_channel(channel_id)
            if str(channel.name) != channel_name:
                await channel.edit(name=channel_name)
                print('Rename project channel {}'.format(channel_name))

    # Archive
    for category_channel_id in category_channel_id_list:
        if len(project_name_list) == len([i for i in channel_id_list if i.isnumeric()]):
            if not category_channel_id in [int(i) for i in channel_id_list]:
                channel = bot.get_channel(category_channel_id)
                channel_name = channel.name
                new_channel_name = channel_name.replace(prefix_ready, prefix_archive)
                if channel_name != new_channel_name:
                    await channel.edit(name=new_channel_name)
                    print('Re-status project channel {}'.format(channel_name))
        else:
            pass

    #Sync Node Meeting (Voice Channel)
    meeting_category = [i for i in categories if 'node' in (i.name).lower() and 'meeting' in (i.name).lower()][0]
    project_category = [i for i in categories if 'node' in (i.name).lower() and 'project' in (i.name).lower()][0]
    meeting_channels = meeting_category.channels
    project_channels = project_category.channels
    v_channel_timeout_days = 1

    for proj_channel in project_channels:
        if not prefix_ready in str(proj_channel):
            continue

        v_channel_name = proj_channel.name + '-voice'
        v_channel_name = v_channel_name.replace(prefix_ready, prefix_voice)

        last_meesage_list = [message async for message in proj_channel.history(limit=1)]

        is_active = True
        if last_meesage_list == []:
            is_active = False
            continue
        last_meesage = last_meesage_list[0]
        inactive_days = (dt.datetime.now() - last_meesage.created_at).days
        #print(inactive_days, v_channel_timeout_days)
        if inactive_days > v_channel_timeout_days:
            is_active = False

        is_exists = v_channel_name in [i.name for i in meeting_channels]
        if not is_exists and is_active:
            meeting_channels.append(
                await guild.create_voice_channel(v_channel_name, category=meeting_category, sync_permissions=True)
            )

        v_channel_find = [i for i in meeting_channels if i.name == v_channel_name]
        if v_channel_find == []:
            continue
        v_channel = v_channel_find[0]

        if not is_active:
            await v_channel.delete()
            continue

        if not is_exists and is_active:
            for member in proj_channel.members:
                await v_channel.set_permissions(
                    member,
                    view_channel=True,
                    connect=True,
                    speak=True
                )

    # Delete Meeting Channel
    del_v_channels = [i for i in meeting_channels if not prefix_voice in i.name]
    for v_channel in del_v_channels:
        await v_channel.delete()

@tasks.loop(minutes=1)
async def auto_translate(alphabet_count=190):
    alphabet_dict = {
        'en' : list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'th' : list('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮะาำเแโใไัี๊่๋้็ิื์')
    }
    #alphabet_list = list(alphabet_dict['en'])

    guild = bot_func.get_guild()
    text_channels = [i for i in guild.channels if str(i.type) == 'text']
    message_list = []
    for channel in text_channels:
        channel_id = channel.id
        messages = [message async for message in channel.history(limit=1)]
        if messages == []:
            continue
        if str(messages[0].author) == str(bot.user):
            continue

        message_content = (messages[0].clean_content).strip()
        message_created_at = str(messages[0].created_at)
        message_id = messages[0].id
        message_author = messages[0].author.nick
        if message_author == None:
            message_author = messages[0].author.name

        eng_alpha = ''.join([i for i in str(message_content) if i in alphabet_dict['en']])
        th_alpha = ''.join([i for i in str(message_content) if i in alphabet_dict['th']])

        #print(eng_alpha)
        #print(th_alpha)

        target_lang = 'th'
        if len(th_alpha) > len(eng_alpha):
            target_lang = 'en'
        elif len(th_alpha) == len(eng_alpha):
            continue

        if alphabet_count > max([len(th_alpha), len(eng_alpha)]):
            continue

        print(channel.name, 'en', len(eng_alpha), 'th', len(th_alpha),'tsl_to',target_lang)

        message_list.append([
            message_created_at,
            message_content,
            message_author,
            channel_id,
            message_id,
            target_lang
        ])

    message_list = sorted(message_list, reverse=True)

    if message_list == []:
        return None

    last_msg = message_list[0]
    last_msg_content = last_msg[1]
    last_msg_author = last_msg[2]
    last_msg_author = last_msg[2]
    channel_id = last_msg[3]
    last_msg_target_lang = last_msg[5]
    print('found last message', last_msg)

    translate_result = bot_func.get_translate(last_msg_content, last_msg_target_lang)
    if translate_result == None:
        return None
    translate_result = translate_result.strip()
    print(translate_result)

    msg = f'''
{last_msg_author} auto translation to {last_msg_target_lang}:
{translate_result}
command `!translate [copy id / copy message link] [en / th]`
'''

    #print(msg)
    channel = bot.get_channel(channel_id)
    await channel.send(msg)

    log_channel = bot.get_channel(channel_dict['log'])
    await log_channel.send( '\n'.join(['found last message in [{}] translate'.format(str(channel.name)),'target lang : {}'.format(last_msg_target_lang)]) )
    """
    # print(message)
    print(message.content)

    eng_alpha = ''.join([i for i in str(message.content) if i in alphabet_list])
    # print('eng alpha', len(eng_alpha), eng_alpha)
    """

@tasks.loop(minutes=30)
async def vote_report():
    guild = bot_func.get_guild()
    text_channels = [i for i in guild.channels if str(i.type) == 'text']
    for channel in text_channels:
        channel_id = channel.id
        bot_messages = [message async for message in channel.history(limit=50)]
        bot_messages = [i for i in bot_messages if bot.user == i.author]
        if bot_messages == []:
            continue

        vote_ref_msg_list = [i for i in bot_messages if 'vote_ref' in str(i.clean_content).split('\n')[-1]]

        for bot_message in vote_ref_msg_list:
            content = bot_message.clean_content
            vote_ref = content.split('\n')[-1]
            vote_ref = int(vote_ref.split('-')[-1])
            #print(vote_ref,content)

            ref_id_list = [message.id async for message in channel.history(limit=15)]
            if not vote_ref in ref_id_list:
                await bot_message.delete()
                continue

            partial_message = channel.get_partial_message(vote_ref)
            question_message = await partial_message.fetch()
            reactions = question_message.reactions
            #print(reactions)

            up_count = [i for i in reactions if i.emoji == '🔼'][0].count - 1
            down_count = [i for i in reactions if i.emoji == '🔽'][0].count - 1
            #print(up_count, down_count)

            if sum([up_count, down_count]) != 0:
                up_percentage = up_count/sum([up_count, down_count])
                up_percentage = round(up_percentage * 100)
                down_percentage = down_count/sum([up_count, down_count])
                down_percentage = round(down_percentage * 100)
                #print(up_percentage, down_percentage)

            else:
                up_percentage, down_percentage = [0,0]

            up_bar = '▓' * int(round(up_percentage / 8))
            down_bar = '▓' * int(round(down_percentage / 8))
            # print(up_bar, down_bar)
            up_count_text = '{:0>2d}'.format(up_count)
            down_count_text = '{:0>2d}'.format(down_count)

            msg = f'''
🔼   {up_bar}  {up_count_text}  ({up_percentage}%)
🔽   {down_bar}  {down_count_text}  ({down_percentage}%)

vote_ref-{question_message.id}
'''
            await bot_message.edit(content=msg)
    print('voting updated')

@tasks.loop(minutes=1)
async def dm_finance_document():
    members = bot_func.get_guild().members
    member_rec = bot_func.get_notino_db('member')
    project_rec = bot_func.get_notino_db('project')
    type_dict = {
        'quotation' : 'ใบเสนอราคา',
        'billing' : 'ใบเสนอราคา',
        'invoice' : 'ใบแจ้งหนี้/ใบเสร็จรับเงิน'
    }

    file_storage_dir = production_manager.file_storage_dir
    project_id_list = os.listdir(file_storage_dir)
    #print(project_id_list)
    for project_id in project_id_list:
        if not project_id in [str(i['page_id']).replace('-','') for i in project_rec]:
            continue
        project_sl = [i for i in project_rec if str(i['page_id']).replace('-','') == project_id][0]
        pdf_dir = file_storage_dir + os.sep + project_id
        pdf_list = os.listdir(pdf_dir)
        pdf_list = [i for i in pdf_list if i.split('_')[-1].replace('.pdf','') in list(type_dict)]
        #print(pdf_list)

        for file in pdf_list:
            file_path = (pdf_dir+os.sep+file).replace('\\','/')
            #print(file_path)
            member_id = file.replace('.pdf','').split('_')[0]
            doc_type = file.replace('.pdf','').split('_')[-1]
            #print(member_id)
            member_sl = [i for i in member_rec if i['page_id'] == member_id][0]
            #pprint.pprint(member_sl)
            discord_id = member_sl['discord_id']
            #print(discord_id)
            member = [i for i in members if i.id == int(discord_id)][0]
            #print(member)

            time.sleep(1)
            msg = f'''
**{project_sl['title']}**
กรุณาตรวจสอบและเซ็นเอกสาร {type_dict[doc_type]} แล้วส่งกลับมาที่ลิงค์ด้านล่างนี้
Please sign {doc_type} and send back to the link below message.
'''
            message = await member.send(msg, file=discord.File(file_path))

            doc_name = '{} Sent {}'.format(member_sl['title'], doc_type.capitalize())
            form_param = urllib.parse.urlencode({
                'usp': 'pp_url',
                'entry.21514028': doc_name,  # document_name
                'entry.539277546': member_id,  # member_nt_ref
                'entry.1860269556': project_id,  # project_nt_ref
                'entry.781252395': discord_id,  # member_dc_ref
                'entry.277609094': message.id,  # message_ref
                'entry.975867958': 'financial'  # document_type
            })
            form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeq6iGMdZfAsputj3mo48OlFdTYck8APClpjDkSOk6dMbZq5A/viewform?' + form_param
            embed = discord.Embed(title=f'Send {doc_type.capitalize()} Document', url=form_url,
                                  description='with Node eDoc Uploader',color=0x16CCFF)
            await message.edit(embed=embed)

            if not os.path.exists(pdf_dir+'/dm'):
                os.makedirs(pdf_dir+'/dm')
            shutil.move(file_path, pdf_dir + '/dm' + os.sep + file)

@tasks.loop(minutes=3)
async def dm_finance_review():
    members = bot_func.get_guild().members
    r_data = production_manager.finance.get_document_review()
    project_rec = bot_func.get_notino_db('project')
    #print(r_data)
    #pprint.pprint(project_rec)

    for data in r_data:
        project_sl = [ i for i in project_rec if i['page_id'] == data['project_nt_ref'] ][0]
        #pprint.pprint(project_sl)
        recruiter_name = project_sl['recruiter_name']
        recruiter_discord_id = int(project_sl['recruiter_discord_id'])
        #print(recruiter_discord_id, type(recruiter_discord_id))
        member = [i for i in members if (i.nick == recruiter_name) or (str(i.id) == str(recruiter_discord_id))][0]
        print('sending review message to {}'.format(member))

        time.sleep(1)
        msg = f'''
**{project_sl['title']}** - {data['document_name']}
Please review {data['document_type']} document
'''
        embed = discord.Embed(title='Review', url=data['document_file'],
                              description=data['document_name'],color=0xA628E3)
        await member.send(msg, embed=embed)

@tasks.loop(hours=24)
async def auto_clear_all_dm_message():
    guild = bot_func.get_guild()
    members = guild.members

    all_direct_messages = []
    for member in members:
        if member == bot.user:
            continue
        messages = [message async for message in member.history(limit=50)]
        messages = [i for i in messages if i.author == bot.user]

        #print(messages)
        all_direct_messages = all_direct_messages + messages
    #print(all_direct_messages)
    for message in all_direct_messages:
        #print('delete',message.created_at,message)
        create_at = message.created_at
        days = (dt.datetime.now() - create_at).days
        #print(create_at, days)
        if days >= 45:
            await message.delete()

@tasks.loop(minutes=30)
async def members_stat_record():
    prev_dir = os.sep.join(base_path.split(os.sep)[:-1])
    rec_dir = prev_dir + '/discord_rec'
    date_time = dt.datetime.now()
    isoweekday, hour = (date_time.isoweekday(),date_time.hour)
    member_stat_csv = rec_dir + '/dc_members_stat_{}_{}.csv'.format(isoweekday,hour)
    message_stat_csv = rec_dir + '/dc_messages_stat_{}_{}.csv'.format(isoweekday,hour)
    if not os.path.exists(rec_dir):
        os.makedirs(rec_dir)

    guild = bot_func.get_guild()
    text_channels = [i for i in guild.channels if str(i.type) == 'text']
    members = guild.members

    df_msg = pd.DataFrame()
    message_list = []
    for channel in text_channels:
        channel_id = channel.id
        messages = [message async for message in channel.history(limit=100)]
        message_list += messages

    for message in message_list:
        create_at = message.created_at
        days = (dt.datetime.now() - create_at).days
        if days > 1 or message.author.bot:
            continue
        df_msg = df_msg.append([{
            'create_at' : create_at,
            'iso_weekday' : create_at.isoweekday(),
            'hour' : create_at.hour,
            'member_name' : message.author.display_name,
            'msg_len' : len(message.clean_content)
        }])
    df_msg.reset_index(inplace=True, drop=True)
    #print(df_msg)
    print('record messages stat')
    df_msg.to_csv(message_stat_csv, index=False)

    df_mb = pd.DataFrame()
    for member in members:
        now = dt.datetime.now()
        df_mb = df_mb.append([{
            'date_time' : now,
            'iso_weekday': now.isoweekday(),
            'hour': now.hour,
            'member_name': member.display_name,
            'is_on_mobile': int(member.is_on_mobile()),
            'raw_status': member.raw_status,
            'is_online': int(member.raw_status == 'online'),
            'is_idle': int(member.raw_status == 'idle'),
            'is_dnd': int(member.raw_status == 'dnd'),
        }])
    df_mb.reset_index(inplace=True, drop=True)
    #print(df_mb)
    print('record members stat')
    if df_mb.empty and os.path.exists(member_stat_csv):
        os.remove(member_stat_csv)
        return None
    df_mb.to_csv(member_stat_csv, index=False)

@tasks.loop(minutes=9)
async def members_stat_report():
    prev_dir = os.sep.join(base_path.split(os.sep)[:-1])
    rec_dir = prev_dir + '/discord_rec'
    date_time = dt.datetime.now()
    isoweekday, hour = (date_time.isoweekday(),date_time.hour)
    week_num = date_time.isocalendar()[1]

    report_time_h = [9]
    report_time_m = [i for i in range(30,38+1)]

    is_report_time = int(date_time.hour) in report_time_h and\
                     int(date_time.minute) in report_time_m and\
                     int(isoweekday) in [1]
    #print('is_report_time', is_report_time)
    if not is_report_time:
        return

    path_list = [rec_dir + os.sep + i for i in os.listdir(rec_dir) if '.csv' in i]

    df = pd.DataFrame()
    for f in path_list:
        try:
            pd.read_csv(f)
        except:
            continue
        df = df.append(pd.read_csv(f))
    #print(df.head(5))
    #print(df.tail(5))

    group_list = ['member_name']
    day_list = ['','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    hour_period_dict = {
        'night' : [i for i in range(21,23+1)] + [i for i in range(0,4+1)],
        'morning' : [i for i in range(5,11+1)],
        'afternoon' : [i for i in range(12,16+1)],
        'evening' : [i for i in range(17,20+1)]
    }
    day_period_dict = {
        'weekDays' : day_list[1:5+1],
        'weekEnds' : day_list[6:7+1]
    }
    col_msg_day_list = []

    # Drop Dup First
    df.drop_duplicates(subset=group_list + ['date_time', 'create_at'], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # New Col
    for i in range(len(day_list)):
        if i == 0:continue;
        msg_col = 'msg_'+day_list[i][:3].lower()+'_percentile'
        df.loc[df['iso_weekday'] == i, 'day_of_week'] = day_list[i]
        df.loc[df['iso_weekday'] == i, msg_col] = 1
        col_msg_day_list.append(msg_col)
    for i in day_period_dict:
        df.loc[df['day_of_week'].isin(day_period_dict[i]), 'period_day'] = i
    for i in hour_period_dict:
        df.loc[df['hour'].isin(hour_period_dict[i]), 'period_hour'] = i

    # Summarise
    df['day_of_week'] = df.dropna(subset=['create_at']).groupby(group_list + ['create_at'])['day_of_week'].transform('max')
    df['period_day'] = df.dropna(subset=['create_at']).groupby(group_list + ['create_at'])['period_day'].transform('max')
    df['period_hour'] = df.dropna(subset=['create_at']).groupby(group_list + ['create_at'])['period_hour'].transform('max')
    df['day_of_week'] = df.groupby(group_list)['day_of_week'].transform('first')
    df['period_day'] = df.groupby(group_list)['period_day'].transform('first')
    df['period_hour'] = df.groupby(group_list)['period_hour'].transform('first')
    df['msg_count'] = df.dropna(subset=['create_at']).groupby(group_list + ['create_at'])['create_at'].transform('count')
    df['msg_count'] = df.groupby(group_list)['msg_count'].transform('sum')
    df['msg_count'] = df['msg_count'].fillna(0.0).round(0)
    df['is_online'] = df.groupby(group_list)['is_online'].transform('sum')
    df['is_idle'] = df.groupby(group_list)['is_idle'].transform('sum')
    df['is_dnd'] = df.groupby(group_list)['is_dnd'].transform('sum')
    df['is_on_mobile'] = df.groupby(group_list)['is_on_mobile'].transform('sum')
    df['msg_len'] = df.groupby(group_list)['msg_len'].transform('sum')
    df['date_time'] = df.groupby(group_list)['date_time'].transform('last')
    for i in col_msg_day_list:
        df[i] = df.dropna(subset=['create_at']).groupby(group_list + ['create_at'])[i].transform('count')
        df[i] = df.groupby(group_list)[i].transform('sum')
        #if df[i].max() == 0.0:continue;
        #df[i] = (df[i] / df[i].max()).round(2)
        df[i] = (df[i] / df['msg_count']).round(2)
        #df[i].fillna(.0, inplace=True)

    # Drop Dup
    df.drop_duplicates(subset=group_list, inplace=True)

    # Calculate
    total_online_count = (df['is_online'] + df['is_idle'] - df['is_on_mobile'])
    #df['fulltime_ratio'] = (total_online_count / 40.0).round(2)
    #df.loc[df['fulltime_ratio'] > 1.0, 'fulltime_ratio'] = 1.0
    #df['parttime_ratio'] = (1 - df['fulltime_ratio']).round(2)
    df['msg_per_day'] = (df['msg_len'] / df['msg_count']).fillna(0.0) / 7.0
    df['msg_per_day'] = df['msg_per_day'].round(0)
    df['online_ratio'] = (total_online_count / (24 * 7)).round(2)
    df.loc[df['online_ratio'] > 1.0, 'online_ratio'] = 1.0
    df['offline_ratio'] = (1 - df['online_ratio']).round(2)
    df['active_ratio'] = (df['online_ratio']/df['online_ratio'].max()) * (df['msg_per_day']/df['msg_per_day'].max())
    df['active_ratio'] = df['active_ratio'].round(2)
    df['inactive_ratio'] = (1 - df['active_ratio']).round(2)

    df.reset_index(inplace=True, drop=True)
    for i in df['member_name'].index.tolist():
        row = df.iloc[i]
        d_list = [dd[0] for dd in day_list[1:]]
        for col in col_msg_day_list:
            index = col_msg_day_list.index(col)
            row = df.iloc[i]
            if row[col] >= 0.15:
                d_list[index] = '**{}**'.format(d_list[index].lower())
            else:
                d_list[index] = '*{}*'.format(d_list[index].lower())
            #print(d_list)
        df.loc[df.index == i, 'day_active'] = ' '.join(d_list)

    # Bar & Fix Row
    ratio_bar_total = 14
    abc = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.')

    df.reset_index(inplace=True, drop=True)
    for i in df['member_name'].index.tolist():
        str_name_list = [i for i in list(df.iloc[i]['member_name']) if i in abc]
        df.loc[df.index == i, 'member_name'] = ''.join(str_name_list)
        df.loc[df.index == i, 'online_bar'] = '▓' * int(round(df.iloc[i]['online_ratio'] * ratio_bar_total,0)) + \
                                                '░' * int(round(df.iloc[i]['offline_ratio'] * ratio_bar_total,0))
        df.loc[df.index == i, 'active_bar'] = '▓' * int(round(df.iloc[i]['active_ratio'] * ratio_bar_total,0)) + \
                                                '░' * int(round(df.iloc[i]['inactive_ratio'] * ratio_bar_total,0))

    df.sort_values(by=['active_ratio','online_ratio'], ascending=[False,False], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # DF Filter
    print(df)
    df = df[df['active_ratio'] != 0.00]

    text1_list = [f'=================\nTOTAL TIME ONLINE ( WEEK-{week_num} )\n=================']
    df.sort_values(by=['online_ratio'], ascending=[False], inplace=True)
    df.reset_index(inplace=True, drop=True)
    for i in df['member_name'].index.tolist():
        row = df.iloc[i]
        text1_list += ['{} {}'.format(row['online_bar'], row['member_name'])]
    text1_join = '\n'.join(text1_list)
    print(text1_join,'\n', len(text1_join))

    text2_list = [f'=================\nON SERVER ACTIVITY ( WEEK-{week_num} )\n=================']
    df.sort_values(by=['active_ratio'], ascending=[False], inplace=True)
    df.reset_index(inplace=True, drop=True)
    for i in df['member_name'].index.tolist():
        row = df.iloc[i]
        text2_list += ['{} {}'.format(row['active_bar'], row['member_name'])]
    text2_join = '\n'.join(text2_list)
    print(text2_join,'\n', len(text2_join))

    text3_list = [f'=================\nPRIME TIME ( WEEK-{week_num} )\n=================']
    df.sort_values(by=['active_ratio'], ascending=[False], inplace=True)
    df.reset_index(inplace=True, drop=True)
    for i in df['member_name'].index.tolist():
        row = df.iloc[i]
        text3_list += ['{}---------------'.format(row['member_name'])]
        text3_list += ['{} ({}), {}'.format(row['period_day'], row['day_active'], row['period_hour'])]
    text3_join = '\n'.join(text3_list)
    print(text3_join, '\n', len(text3_join))

    channel = bot.get_channel(channel_dict['report'])
    await channel.send(text1_join[:2000])
    await channel.send(text2_join[:2000])
    await channel.send(text3_join[:2000])

"""---------------------------------"""
# Discord Command
"""---------------------------------"""
@bot.command()
async def dev_data(ctx):
    ctx_data = bot_func.get_ctx_data(ctx)
    data_str = json.dumps(ctx_data, indent=4)
    await ctx.send('`{}`'.format(data_str), delete_after=15)
    await ctx.message.delete(delay=0)
    print(data_str)

@bot.command()
async def sys_update(ctx):
    await ctx.send('system update', delete_after=2)
    await ctx.message.delete()
    if not os.name == 'nt':
        import raspi_update
        importlib.reload(raspi_update)
        raspi_update.update()

@bot.command()
async def sys_reboot(ctx):
    await ctx.send('system reboot', delete_after=2)
    await ctx.message.delete()
    if not os.name == 'nt':
        os.system('sudo reboot')

@bot.command()
async def dev_test(ctx):
    await ctx.send('got your command !', mention_author=True, tts=True, delete_after=5)
    await ctx.message.delete(delay=0)
    ctx_data = bot_func.get_ctx_data(ctx)
    task_name = 'do_nothing'
    task_data = {
        'member_id': ctx_data['author']['id'],
        'member_name': ctx_data['author']['name']
    }
    bot_func.add_queue_task(task_name, task_data)

@bot.command()
async def translate(ctx, copy_id, target_lang):
    target_dict = {'th': 'Thai', 'en': 'English'}
    target_lang = target_lang.lower()
    if not target_lang in list(target_dict):
        return None

    if 'http' in copy_id:
        copy_id = copy_id.split('/')[-2:]
    else:
        copy_id = copy_id.strip()
        copy_id = copy_id.split('-')

    channel_id = int(copy_id[0])
    message_id = int(copy_id[-1])

    channel = bot.get_channel(channel_id)
    partial_message = channel.get_partial_message(message_id)
    message = await partial_message.fetch()
    jump_url = message.jump_url
    #msg_content = message.content
    msg_content = message.clean_content
    msg_content = msg_content.strip()
    msg_author = message.author.nick
    if msg_author == None:
        msg_author = message.author.name

    bot_msg = await ctx.send('let\'s me translate...')
    result = bot_func.get_translate(msg_content, target_lang)
    if result == None:
        bot_msg.delete()
        return None
    else:
        embed = discord.Embed(title='see original message', url=jump_url)
        new_msg = f'''
message from **{msg_author}** in {target_dict[target_lang]} language
\"{result}\"
command `!translate [copy id / copy message link] [en / th]`
        '''
        await ctx.message.delete()
        await bot_msg.edit(content=new_msg, embed=embed, tts=True)

@bot.command()
async def vote(ctx, question):
    ctx_data = bot_func.get_ctx_data(ctx)
    #await ctx.message.delete(delay=10)
    print(question)
    #print(ctx.message.content)
    msg = f'''
vote_ref-{ctx_data['message']['id']}
'''
    bot_msg = await ctx.send(msg)
    await ctx.message.add_reaction('🔼')
    await ctx.message.add_reaction('🔽')

    #await bot_msg.edit(content=msg, delete_after=5)

"""---------------------------------"""
# Discord Command Member
"""---------------------------------"""
@bot.command()
async def my_id(ctx):
    ctx_data = bot_func.get_ctx_data(ctx)
    id = ctx_data['author']['id']
    mention = ctx_data['author']['mention']
    await ctx.send(f'{mention}\nyour discord id is\n`{id}`', mention_author=True, delete_after=5*60)
    await ctx.message.delete(delay=0)

@bot.command()
async def my_status(ctx):
    ctx_data = bot_func.get_ctx_data(ctx)
    role_list = [i['name'] for i in ctx_data['author']['roles'] if not 'everyone'in i['name']]
    role_str = ',   '.join(role_list)
    mention = ctx_data['author']['mention']
    id = ctx_data['author']['id']
    embed = embed=discord.Embed(
        #title='Member Register/Update', url='https://forms.gle/QrqycQV75o4xRJ4ZA',
        title='Member Register/Update',
        url='https://docs.google.com/forms/d/e/1FAIpQLSdFyzv8sUaNelC-IQuEEkQ0jc-oo9KgIoWP3q6qaF7OOFjruQ/viewform',
        description='You are not in \"Node Freelance\" Role, Please submit this form',
        color=0xFF5733)
    msg = f'{mention}\n' \
          f'Discord ID : `{id}`\n' \
          f'Roles : {role_str}\n'
          #f'\n' \
    if 'Node Freelance' in role_list:
        await ctx.send(msg + '\nYou are already in the \"Node Freelance\" Role', mention_author=True, delete_after=20)
    else:
        await ctx.send(msg, mention_author=True, embed=embed, delete_after=180)
    await ctx.message.delete(delay=0)

@bot.command()
async def register(ctx):
    ctx_data = bot_func.get_ctx_data(ctx)
    member = ctx.author
    mention = ctx_data['author']['mention']
    name = ctx_data['author']['name']
    embed = embed = discord.Embed(
        #title='Member Register/Update', url='https://forms.gle/QrqycQV75o4xRJ4ZA',
        title='Member Register/Update', url='https://docs.google.com/forms/d/e/1FAIpQLSdFyzv8sUaNelC-IQuEEkQ0jc-oo9KgIoWP3q6qaF7OOFjruQ/viewform',
        description='',
        color=0xFF5733)
    await ctx.send(f'{mention}', mention_author=True, embed=embed, delete_after=5*60)
    await ctx.message.delete(delay=0)

@bot.command()
async def join(ctx, project_name, hour_week):
    #await ctx.message.delete(delay=0)
    ctx_data = bot_func.get_ctx_data(ctx)
    id = ctx_data['author']['id']
    mention = ctx_data['author']['mention']

    msg = f'{mention} sent your task to queue\n' \
          f'Project : {project_name}\n' \
          f'Hours per week : {hour_week}\n'\
          f'going to add you to the project soon.'
    await ctx.send(f'{msg}', mention_author=True, delete_after=60)
    task_name = 'join_project'
    task_data = {
        'discord_id': ctx_data['author']['id'],
        'project_name': project_name,
        'hour_week': float(hour_week)
    }
    bot_func.add_queue_task(task_name, task_data)

@bot.command()
@commands.has_role('Node Recruiter')
async def finance(ctx, doc_type):
    doc_type = doc_type.lower()
    await ctx.message.delete(delay=0)
    ctx_data = bot_func.get_ctx_data(ctx)
    channel_id = ctx_data['channel']['id']
    mention = ctx_data['author']['mention']
    projects = bot_func.get_notino_db('project')
    finances = bot_func.get_notino_db('project_finance')

    type_list = ['quotation', 'billing', 'invoice']
    if not doc_type in type_list:
        #print(f'document type must be in {type_list}')
        await ctx.send(f'{mention}! document type must be in {type_list}', mention_author=True, delete_after=10)
        return None
    if ctx_data['category'] != {} and not 'project' in ctx_data['category']['name'].lower():
        print('can\'t run command because the channel\'s not in Node-Project category')
        await ctx.send(f'{mention}! request\'s not in project channel', mention_author=True, delete_after=10)
        return None

    project_sl = [i for i in projects if str(i['discord_channel_id']) == str(channel_id)][0]
    client_data = {
        'client_name': '',
        'client_address': '',
        'client_tax_id': '',
        'client_contract_name': '',
        'client_phone': '',
        'client_email': ''
    }
    finance_list = [i for i in finances if str(i['name']) == str(project_sl['title'])]
    if finance_list != []:
        finance_sl = finance_list[0]
        for k in client_data:
            client_data[k] = finance_sl[k]
        '''
        client_data['client_name'] = finance_sl['client_name']
        client_data['client_address'] = finance_sl['client_address']
        client_data['client_tax_id'] = finance_sl['client_tax_id']
        client_data['client_contract_name'] = finance_sl['client_contract_name']
        client_data['client_phone'] = finance_sl['client_phone']
        client_data['client_email'] = finance_sl['client_email']
        '''

    msg = f'''
Project : {project_sl['title']}
Document Type : {doc_type.capitalize()}
Please fill out the information for issuing financial documents.
'''

    form_param = urllib.parse.urlencode({
        'usp': 'pp_url',
        'entry.1195174781': project_sl['page_id'],
        'entry.294203430' : ctx_data['author']['id'],
        #'entry.620584290' : member_name,
        'entry.334540373' : project_sl['title'],
        'entry.1543450070' : 1,
        'entry.1362031786' : 'Baht',
        'entry.872234013' : 3,
        'entry.1336336038' : doc_type,
        'entry.741791868' : client_data['client_name'],
        'entry.1419364983' : client_data['client_address'],
        'entry.1563554333' : client_data['client_tax_id'],
        'entry.54552248' : client_data['client_contract_name'],
        'entry.2111754486' : client_data['client_phone'],
        'entry.1855558017' : client_data['client_email']
    })
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSdoHb7WZKZWbJJTfPnwFgozGaiphzSOEjs0WimFVzqhTZAQ5w/viewform?' + form_param
    embed = discord.Embed(title=f'''{project_sl['title']} - {doc_type.capitalize()}''', url=form_url,
                          description='with Node Flow Account', color=0xfcba03)
    await ctx.author.send(msg, embed=embed)
    await ctx.message.delete(delay=10)

    """
    freelance_role = [i for i in ctx_data['guild']['roles'] if i['name'] == 'Node Freelancer'][0]
    msg2 = f'''
{mention}'s working on financial documents.

{freelance_role['mention']} 
Please check and update your account information.
กรุณาอัพเดทข้อมูลข้อมูลที่จำเป็นเกี่ยวกับเอกสารทางการเงิน..
'''
    embed2 = discord.Embed(title='update account information', url='https://forms.gle/QrqycQV75o4xRJ4ZA')
    await ctx.send(msg2, embed=embed2)
    """

"""---------------------------------"""
# Discord Command Recruiter
"""---------------------------------"""
#@bot.command()
#async def new_project(ctx, project_name, hour_week):

@bot.command()
@commands.has_role('Node Recruiter')
async def member_id(ctx, member_mention):
    await ctx.message.delete(delay=10)
    #print(member_mention,type(member_mention))
    if not '@' in member_mention:
        return None
    member_id = int(''.join([i for i in member_mention if i.isdigit()]))
    #print(member_id)
    await ctx.send(f'member id {member_id}', delete_after=10)

@bot.command()
@commands.has_role('Node Recruiter')
async def all_member(ctx):
    await ctx.message.delete()
    ctx_data = bot_func.get_ctx_data(ctx)
    members = bot_func.get_notino_db('member')
    mention = ctx_data['author']['mention']
    regis_rec = bot_func.get_notino_db('member')

    #member_text_list = [ ',  {}  '.format(i['title']) for i in members ]
    member_text_list = [ '{}  -  ID {}  -  *{}*\n'.format(
        i['title'], i['discord_id'], i['hour_week_text']) for i in members ]
    member_text_list = sorted(member_text_list)

    """
    for i in member_text_list:
        index = member_text_list.index(i)
        if index % 3 == 0:
            member_text_list[index] = member_text_list[index] + '\n'
    """
    msg = \
f'''
**All member list**
{''.join(member_text_list)}
'''
    await ctx.author.send(f'{mention}{msg}', mention_author=True, delete_after=30)


@bot.command()
@commands.has_role('Node Recruiter')
async def add(ctx, member_name):
    await ctx.message.delete()
    ctx_data = bot_func.get_ctx_data(ctx)
    channel_id = ctx_data['channel']['id']
    channel = bot.get_channel(channel_id)

    regis_rec = bot_func.get_notino_db('member')
    project_rec = bot_func.get_notino_db('project')
    find_member = [i for i in regis_rec if i['title'] == member_name]
    if len(find_member) == 0:
        await ctx.send(f'member name \"{member_name}\" are not found', delete_after=2)
    else:
        find_member = find_member[0]
        member_id = int(find_member['discord_id'])

        guild = bot_func.get_guild()
        member = [i for i in guild.members if i.id == member_id][0]
        await channel.set_permissions(member, read_messages=True, send_messages=True)
        await ctx.send(f'**{member_name}**   joined channel')

@bot.command()
@commands.has_role('Node Recruiter')
async def remove(ctx, member_name):
    await ctx.message.delete()
    ctx_data = bot_func.get_ctx_data(ctx)
    channel_id = ctx_data['channel']['id']
    channel = bot.get_channel(channel_id)

    regis_rec = bot_func.get_notino_db('member')
    find_member = [i for i in regis_rec if i['title'] == member_name]
    if len(find_member) == 0:
        await ctx.send(f'member name \"{member_name}\" are not found', delete_after=2)
    else:
        find_member = find_member[0]
        member_id = int(find_member['discord_id'])

        guild = bot_func.get_guild()
        member = [i for i in guild.members if i.id == member_id][0]
        await channel.set_permissions(member, read_messages=False, send_messages=False)
        await ctx.send(f'**{member_name}**   leave channel')

"""---------------------------------"""
# On Message
"""---------------------------------"""
@bot.event
async def on_message(message):
    if not message.guild == bot_func.get_guild():
        return None

    member_name = message.author.display_name

    #Image attachment outside from project channel -------------------------------------
    is_bot_self = message.author == bot.user
    is_attachment = message.attachments != []
    is_project_channel = 'proj-' in message.channel.name
    media_ext_list = ['jpg', 'jpeg', 'png', 'gif', 'mov', 'mp4']
    print(message)
    #print(message.channel.name)
    #print(is_attachment and is_project_channel)
    if not is_project_channel and is_attachment and not is_bot_self:
        attach_sl = (message.attachments)[0]
        is_media = attach_sl.url.split('.')[-1] in media_ext_list
        if is_media:
            log_text = f'Found member \"{member_name}\" shared media outside project (\"{message.channel.name}\").'
            log_channel = bot.get_channel(channel_dict['log'])
            await log_channel.send(log_text)

            dm_text = f'**This message was sent to you**\nbecause you just shared some media outside ' \
                      f'(\"{message.channel.name}\") that isn\'t a project channel \nand might be ' \
                      f'risked to confidentiality of project\nplease re-check it again.'
            await message.author.send(dm_text)
            await log_channel.send('sent dm message to member already.')

    # No Command -------------------------------------
    if message.content.startswith('! ') or message.content.startswith('/ '):
        msg = 'Please ensure use ! exclamation mark and command without whitespace.'
        channel = bot.get_channel(message.channel.id)
        await channel.send(msg)

    #TEST EMBED
    if message.content.startswith('!embed'):
        embed = discord.Embed(title="Links", description="Here are 3 links:")
        # Customization for Link 1
        embed.add_field(name="🌐 Link 1", value="https://www.example.com", inline=False)
        # Customization for Link 2
        embed.add_field(name="Link 2", value="https://www.google.com", inline=True)
        # Customization for Link 3
        embed.add_field(name="🎉 Link 3", value="https://www.discord.com", inline=False)
        embed.set_image(url="https://i.imgur.com/fYk81j1.png")

        # Additional customization for the embed
        embed.set_footer(text="Thanks for using our bot!", icon_url="https://i.imgur.com/1Fp6hK5.png")
        embed.set_thumbnail(url="https://i.imgur.com/fYk81j1.png")

        await message.channel.send(embed=embed)

    # Accept Command
    await bot.process_commands(message)


"""---------------------------------"""
# Run
"""---------------------------------"""
loaded = [i.split(':')[0] for i in sys.modules]
for dp in [src_path + os.sep + i for i in os.listdir(src_path + os.sep + 'site-packages_3.10')]:
    #print(dp)
    bname = os.path.basename(dp)
    if '.' in bname: continue
    if not bname in loaded:
        print(bname, bname in loaded)
bot.run(token)