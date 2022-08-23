from discord.ext import commands, tasks
import discord
import requests, os, csv, os, json, time, pprint
import datetime as dt
import pandas as pd

"""
https://discordpy.readthedocs.io/en/stable/api.html
https://autocode.com/tools/discord/embed-builder/
"""
#-------------------------------------
# Init
#-------------------------------------
base_path = os.path.dirname(os.path.abspath(__file__))

config_file_name = os.path.basename(os.path.abspath(__file__)).replace('.py','.json')
with open(base_path + '/' + config_file_name) as config_f:
    config_j = json.load(config_f)
token = config_j['token']
sever_id = config_j['sever_id']

intents = discord.Intents.default()
intents.members = True
client = discord.Client()
bot = commands.Bot(command_prefix='!', intents=intents)
if os.name == 'nt':
    bot = commands.Bot(command_prefix='/', intents=intents)

class botFunction:
    def addQueueTask(task_name, data_dict):
        if type(data_dict) != type(dict()):
            return None
        data = {
            'name': task_name,
            'data': data_dict
        }
        data['data'] = str(data['data'])
        response = requests.post(
            'https://script.google.com/macros/s/'
            'AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJj'
            'j2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec',
            params=data)
        print(response.text)
        print(data)

    def getContextData(ctx):
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
                'name': i.name})
        for i in ctx.author.roles:
            data['author']['roles'].append({
                'id': i.id,
                'name': i.name})
        if ctx.channel.category != None:
            data['category']['name'] = ctx.channel.category.name
            data['category']['id'] = ctx.channel.category.id

        return data

    def getRegisteredMember():
        member_path = os.sep.join(base_path.split(os.sep)[:-1]) + '/production_rec/notionDatabase/csv/member.csv'
        df = pd.read_csv(member_path)
        rec = []
        for i in df.index.tolist():
            row = df.loc[i]
            rec.append(row.to_dict())
        return rec

    def getProjects():
        project_path = os.sep.join(base_path.split(os.sep)[:-1]) + '/production_rec/notionDatabase/csv/project.csv'
        df = pd.read_csv(project_path)
        rec = []
        for i in df.index.tolist():
            row = df.loc[i]
            rec.append(row.to_dict())
        return rec

    def getGuild():
        guild = [bot.guilds[i] for i in range(len(bot.guilds)) if str(bot.guilds[i].id) == sever_id][0]
        return guild



#-------------------------------------
# Discord Start
#-------------------------------------
@bot.event
async def on_ready():
    print('bot online now!')

    channel = bot.get_channel(1011320896063021147)
    await channel.send(f'`{dt.datetime.now()}`\nHello, I just woke up\n(Runnig on os \"{os.name}\")')

    role_update.start()
    project_invite.start()


#-------------------------------------
# Discord Sync
#-------------------------------------
@tasks.loop(seconds=60.0)
async def role_update():
    regis_rec = botFunction.getRegisteredMember()
    regis_id_list = [int(i['discord_id']) for i in regis_rec]
    # print(regis_id_list)
    guild = botFunction.getGuild()
    member_id_list = [i.id for i in guild.members]
    # print(member_id_list)
    member_role = [i for i in guild.roles if 'Freelancer' in i.name][0]
    # print(member_role)
    for member in guild.members:
        member_id = member.id
        #print(member_id, member)
        if member_id in regis_id_list:
            await member.add_roles(member_role)
        else:
            await member.remove_roles(member_role)
    print(dt.datetime.now(), 'member role updated')

@tasks.loop(hours=24)
async def project_invite():
    projects = botFunction.getProjects()
    projects = [ i for i in projects if i['ready_to_invite'] ]
    guild = botFunction.getGuild()
    target_role = [i for i in guild.roles if i.name == 'Node Freelance'][0]
    for project in projects:
        channel = bot.get_channel(1011594327132209193)
        msg = f'''
Hi {target_role.mention}
We have a project you might be interested in.

Project : **{project['title']}**

Reference Link : `{project['reference_link']}`
Project Date : {str(project['project_date']).replace(',',' - ')}

If are you are interested
type `!join [Project Name] [Your availibility hour per week]`

example `!join {project['title'].strip().replace(' ','_')} 20`
    '''
        await channel.send(f'{msg}')

    task_name = 'sent_invite_to_project'
    task_data = {
        'project_name': project['title'],
    }
    botFunction.addQueueTask(task_name, task_data)

#-------------------------------------
# Discord Command
#-------------------------------------
@bot.command()
async def dev_data(ctx):
    ctx_data = botFunction.getContextData(ctx)
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
    ctx_data = botFunction.getContextData(ctx)
    task_name = 'do_nothing'
    task_data = {
        'member_id': ctx_data['author']['id'],
        'member_name': ctx_data['author']['name']
    }
    botFunction.addQueueTask(task_name, task_data)

#-------------------------------------
# Discord Command Member
#-------------------------------------
@bot.command()
async def my_id(ctx):
    ctx_data = botFunction.getContextData(ctx)
    id = ctx_data['author']['id']
    mention = ctx_data['author']['mention']
    await ctx.send(f'{mention}\nyour discord id is\n`{id}`', mention_author=True, delete_after=20)
    await ctx.message.delete(delay=0)

@bot.command()
async def my_status(ctx):
    ctx_data = botFunction.getContextData(ctx)
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
        await ctx.send(msg, mention_author=True, embed=embed, delete_after=20)
    await ctx.message.delete(delay=0)

@bot.command()
async def register(ctx):
    ctx_data = botFunction.getContextData(ctx)
    mention = ctx_data['author']['mention']
    embed = embed = discord.Embed(
        title='Member Register/Update', url='https://forms.gle/QrqycQV75o4xRJ4ZA',
        description='',
        color=0xFF5733)
    await ctx.send(f'{mention}', mention_author=True, embed=embed, delete_after=15)
    await ctx.message.delete(delay=0)

@bot.command()
async def join(ctx, project_name, hour_week):
    await ctx.message.delete(delay=0)
    ctx_data = botFunction.getContextData(ctx)
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
        'hour_week': hour_week
    }
    botFunction.addQueueTask(task_name, task_data)


#-------------------------------------
# Run
#-------------------------------------
bot.run(token)