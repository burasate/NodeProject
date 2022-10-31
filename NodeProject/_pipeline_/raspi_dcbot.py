# -*- coding: utf-8 -*-
from discord.ext import commands, tasks
import discord, urllib
import requests, os, csv, os, json, time, pprint, sys, shutil
import datetime as dt
import pandas as pd
import numpy as np
import urllib.parse

"""
https://discordpy.readthedocs.io/en/stable/api.html
https://autocode.com/tools/discord/embed-builder/
"""
"""---------------------------------"""
# Init
"""---------------------------------"""
base_path = os.path.dirname(os.path.abspath(__file__))
src_path = base_path+'/src'

if not src_path in sys.path:
    sys.path.insert(0,src_path)

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
client = discord.Client()
bot = commands.Bot(command_prefix='!', intents=intents)
if os.name == 'nt':
    bot = commands.Bot(command_prefix='/', intents=intents)

channel_dict = {
    'log' : 1011320896063021147,
    'member_welcome' : 1012248546050846720,
    'welcome' : 920741438516523051
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
        data['data'] = str(data['data']).replace('\'','\"')
        response = requests.post(
            'https://script.google.com/macros/s/'
            'AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJj'
            'j2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec',
            params=data)
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

    """
    def get_register_member():
        member_path = os.sep.join(base_path.split(os.sep)[:-1]) + '/production_rec/notionDatabase/csv/member.csv'
        df = pd.read_csv(member_path)
        rec = []
        for i in df.index.tolist():
            row = df.loc[i]
            rec.append(row.to_dict())
        return rec
    """

    """
    def get_projects():
        project_path = os.sep.join(base_path.split(os.sep)[:-1]) + '/production_rec/notionDatabase/csv/project.csv'
        df = pd.read_csv(project_path)
        rec = []
        for i in df.index.tolist():
            row = df.loc[i]
            rec.append(row.to_dict())
        return rec
    """

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
    print('bot online now!')

    if not os.name == 'nt':
        channel = bot.get_channel(channel_dict['log'])
        await channel.send(f'`{dt.datetime.now()}`\nHello, I just woke up\n(Runnig on os \"{os.name}\")')

        #project_invite.start()
        print_time.start()
        vote_report.start()
        role_update.start()
        project_channel_update.start()
        traceback_nortify.start()
        auto_translate.start()
        dm_finance_document.start()
        dm_finance_review.start()
        auto_clear_all_dm_message.start()

"""---------------------------------"""
# Discord Sync
"""---------------------------------"""
@tasks.loop(minutes=30)
async def print_time():
    print(f'\n==========[     {dt.datetime.now()}     ]==========\n')

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
        print(member.display_name , member_id, is_id_found) #show all member sync
        #'''
        if is_id_found:
            member_sl = [i for i in regis_rec if int(i['discord_id']) == member_id][0]
            user_name = member_sl['title']
            if not is_role_found:
                await member.add_roles(apply_role)
                await member.edit(nick=user_name)

                msg = f'added {user_name} ({member.display_name}) to \"{apply_role.name}\" role'
                if not msg in content_list:
                    await channel.send(f'{msg}')
            if member.nick != user_name:
                await member.edit(nick=user_name)

        elif not is_id_found and is_role_found:
            await member.remove_roles(apply_role)

    print('member role updated')

"""
@tasks.loop(minutes=10)
async def project_invite():
    projects = bot_func.get_notino_db('project')
    projects = [ i for i in projects if i['ready_to_invite'] and not i['sent_invite'] ]
    guild = bot_func.get_guild()
    target_role = [ i for i in guild.roles if 'Node Freelancer' in i.name ][0]
    #channel = bot.get_channel(1011594327132209193) #invite_channel
    channel = bot.get_channel(1010175157119225978) #test_channel

    for project in projects:
        msg = f'''
Hi {target_role.mention}
We have a project you might be interested in.

Project : **{project['title']}**

Reference Link : `{project['reference_link']}`
Project Date : {str(project['project_date']).replace(',',' - ')}

If are you are interested
type `!join [Project Name] [Your availibility hour per week]`

for example
`!join {project['title'].strip().replace(' ','_')} 20`

*then your availibility will re-calculated to register/update form*
    '''
        await channel.send(f'{msg}')

        task_name = 'sent_invite_to_project'
        task_data = {
            'project_name': project['title'],
        }
        bot_func.add_queue_task(task_name, task_data)
"""

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

@tasks.loop(hours=6)
async def traceback_nortify():
    rec = system_manager.error.get_nortify()
    for i in rec:
        msg = \
f'''
🚨 {i['date_time']}
`{str(i['traceback'])[-1900:]}`
'''
        channel = bot.get_channel(channel_dict['log'])
        await channel.send(f'{msg}')

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

            ref_id_list = [message.id async for message in channel.history(limit=100)]
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
        project_sl = [i for i in project_rec if i['page_id'] == project_id][0]
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
        if days >= 15:
            await message.delete()

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
    await ctx.send(f'{mention}\nyour discord id is\n`{id}`', mention_author=True, delete_after=20)
    await ctx.message.delete(delay=0)

@bot.command()
async def my_status(ctx):
    ctx_data = bot_func.get_ctx_data(ctx)
    role_list = [i['name'] for i in ctx_data['author']['roles'] if not 'everyone'in i['name']]
    role_str = ',   '.join(role_list)
    mention = ctx_data['author']['mention']
    id = ctx_data['author']['id']
    embed = embed=discord.Embed(
        title='Member Register/Update', url='https://forms.gle/QrqycQV75o4xRJ4ZA',
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
    mention = ctx_data['author']['mention']
    embed = embed = discord.Embed(
        title='Member Register/Update', url='https://forms.gle/QrqycQV75o4xRJ4ZA',
        description='',
        color=0xFF5733)
    await ctx.send(f'{mention}', mention_author=True, embed=embed, delete_after=15)
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

"""
@bot.command()
@commands.has_role('Node Recruiter')
async def finance(ctx, doc_type):
    doc_type = doc_type.lower()
    await ctx.message.delete(delay=0)
    ctx_data = bot_func.get_ctx_data(ctx)
    mention = ctx_data['author']['mention']

    type_list = ['quotation', 'billing', 'invoice']
    if not doc_type in type_list:
        #print(f'document type must be in {type_list}')
        await ctx.send(f'{mention}! document type must be in {type_list}', mention_author=True, delete_after=10)
        return None
    if ctx_data['category'] != {} and not 'project' in ctx_data['category']['name'].lower():
        print('can\'t run command because the channel\'s not in Node-Project category')
        await ctx.send(f'{mention}! request\'s not in project channel', mention_author=True, delete_after=10)
        return None

    task_name = 'generate_financial_document'
    task_data = {
        #'member_id': ctx_data['author']['id'],
        'member_name': ctx_data['author']['nick'],
        'channel_id': ctx_data['channel']['id'],
        'document_type' : doc_type
    }
    bot_func.add_queue_task(task_name, task_data)
    await ctx.send(f'{mention} sent request for {doc_type.capitalize()} document\nเอกสารจะถูกส่งไปที่ข้อความส่วนตัวเพื่อให้ตรวจสอบ..', mention_author=True)
"""

@bot.command()
@commands.has_role('Node Recruiter')
async def finance(ctx, doc_type):
    doc_type = doc_type.lower()
    await ctx.message.delete(delay=0)
    ctx_data = bot_func.get_ctx_data(ctx)
    channel_id = ctx_data['channel']['id']
    mention = ctx_data['author']['mention']
    projects = bot_func.get_notino_db('project')

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
        'entry.1336336038' : doc_type
    })
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSdoHb7WZKZWbJJTfPnwFgozGaiphzSOEjs0WimFVzqhTZAQ5w/viewform?' + form_param
    embed = discord.Embed(title=f'''{project_sl['title']} - {doc_type.capitalize()}''', url=form_url,
                          description='with Node Flow Account', color=0xfcba03)
    await ctx.author.send(msg, embed=embed)

    freelance_role = [i for i in ctx_data['guild']['roles'] if i['name'] == 'Node Freelancer'][0]
    msg2 = f'''
{mention}'s working on financial documents.

{freelance_role['mention']} 
Please check and update your account information.
กรุณาอัพเดทข้อมูลข้อมูลที่จำเป็นเกี่ยวกับเอกสารทางการเงิน..
'''
    embed2 = discord.Embed(title='update account information', url='https://forms.gle/QrqycQV75o4xRJ4ZA')
    await ctx.send(msg2, embed=embed2)

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
    member_text_list = [ '{}  -  *{}*\n'.format(i['title'], i['hour_week_text']) for i in members ]

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

"""
@bot.command()
@commands.has_role('Node Recruiter')
async def project_member(ctx):
    await ctx.message.delete()
    ctx_data = bot_func.get_ctx_data(ctx)
    projects = bot_func.get_notino_db('project')
    proj_ch_id_list = [i['discord_channel_id'] for i in projects]
    proj_list = [i['title'] for i in projects]
    channel_id = ctx_data['channel']['id']
    mention = ctx_data['author']['mention']

    if channel_id in proj_ch_id_list:
        project_member = bot_func.get_notino_db('project_member')
        project_sl = proj_list[proj_ch_id_list.index(channel_id)]

        project_member = [ i for i in project_member if i['project'].lower() == project_sl.lower() ]
        member_text_list = [
            '{}  -  available {} week'.format(i['member'], i['hour_week']) + '\n`!add {}`\n'.format(i['member'])
            for i in project_member
        ]
        msg = \
f'''
**Members who has interested this project**

{''.join(member_text_list)}

for remove member 
typ `!remove [Name]`
'''
        await ctx.send(f'{mention}{msg}', mention_author=True, delete_after=180)
"""

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
    is_attachment = message.attachments != []
    is_project_channel = 'proj-' in message.channel.name
    media_ext_list = ['jpg', 'jpeg', 'png', 'gif', 'mov', 'mp4']
    #print(message)
    #print(message.channel.name)
    #print(is_attachment and is_project_channel)
    if not is_project_channel and is_attachment:
        attach_sl = (message.attachments)[0]
        is_media = attach_sl.url.split('.')[-1] in media_ext_list
        if is_media:
            log_text = f'Found member \"{member_name}\" shared media outside project (\"{message.channel.name}\").'
            log_channel = bot.get_channel(channel_dict['log'])
            await log_channel.send(log_text)

            dm_text = f'**Just notice to you**\nbecause you just shared some media outside ' \
                      f'(\"{message.channel.name}\") that isn\'t a project channel \nand might be ' \
                      f'risked to confidentiality of project\nplease re-check it again.'
            await message.author.send(dm_text)
            await log_channel.send('sent dm message to member already.')

    # Accept Command
    await bot.process_commands(message)

"""---------------------------------"""
# Run
"""---------------------------------"""
bot.run(token)