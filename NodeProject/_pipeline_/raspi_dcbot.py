from discord.ext import commands, tasks
import discord
import requests, os, csv, os, json
import datetime as dt

"""
https://discordpy.readthedocs.io/en/stable/api.html
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
intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client()

#import botFunction
#botFunction.addQueueTask( task_name, data_dict )

#-------------------------------------
# Context Data
#-------------------------------------
#botFunction.getContextData(ctx)

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
            'category': {
                'name': ctx.channel.category.name,
                'id': ctx.channel.category_id,
            },
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
        return data

    def getRegisteredMember():
        member_path = os.sep.join(base_path.split(os.sep)[:-1]) + '/production_rec/notionDatabase/csv/member.csv'
        #print(member_path)

        with open(member_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            rec = [dict(i) for i in csv_reader if dict(i)['discord_id'] != '']
        return rec

#-------------------------------------
# Discord Start
#-------------------------------------
@bot.event
async def on_ready():
    print('bot online now!')
    role_update.start()


#-------------------------------------
# Discord Sync
#-------------------------------------
@tasks.loop(seconds=5.0)
async def role_update():
    regis_rec = botFunction.getRegisteredMember()
    regis_id_list = [int(i['discord_id']) for i in regis_rec]
    # print(regis_id_list)
    guild = [bot.guilds[i] for i in range(len(bot.guilds)) if str(bot.guilds[i].id) == sever_id][0]
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

#-------------------------------------
# Discord Command
#-------------------------------------
@bot.command()
async def data(ctx):
    ctx_data = botFunction.getContextData(ctx)
    data_str = json.dumps(ctx_data, indent=4)
    await ctx.send('`{}`'.format(data_str), delete_after=15)
    await ctx.message.delete(delay=2.5)
    print(data_str)

@bot.command()
async def test(ctx):
    await ctx.send('got your command !', mention_author=True, tts=True, delete_after=5)
    await ctx.message.delete(delay=2.5)
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
    await ctx.send(f'{mention}\nyour discord id is\n`{id}`', mention_author=True, delete_after=10)
    await ctx.message.delete(delay=0)

@bot.command()
async def my_status(ctx):
    ctx_data = botFunction.getContextData(ctx)
    role = ', '.join([i['name'] for i in ctx_data['author']['roles'] if not 'everyone'in i['name']])
    nick = ctx_data['author']['nick']
    msg = f'{nick}\n' \
          f'role : {role}\n'
          #f'\n' \
    await ctx.send(msg, mention_author=True, delete_after=10)
    await ctx.message.delete(delay=0)

#-------------------------------------
# Run
#-------------------------------------
bot.run(token)