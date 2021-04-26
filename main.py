import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
intents.members = True
prefix = 'pp '

load_dotenv()
dTOKEN = os.getenv('dTOKEN')
client = commands.Bot(command_prefix=prefix,
                      intents=intents, owner_id=int(os.getenv('OwnerID')))

# cog_list from all .py files in folder cogs
cogs = [fn[:-3] for fn in os.listdir(os.path.join(
        './', 'cogs')) if fn.endswith('.py')]

# cog loader
for cog in cogs:
    if cog in ['testing', 'leveling']:
        try:
            client.load_extension(f'cogs.{cog}')
        except Exception as e:
            print(f'Could not load cog {cog}: {str(e)}')
        else:
            print(f'{cog} cog loaded')


async def list_guilds():
    temp = ('--- Bot Servers Joined ---\n')
    count = 0
    async for guild in client.fetch_guilds(limit=150):
        count += 1
        temp = temp+(f'Guild {guild.name} : ({guild.id}) ')
    temp = temp+(f'\nLogged in to {count} Discord Servers')
    return temp


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f'for {prefix} command'))
    console_msg = await list_guilds()
    print(console_msg)


client.run(dTOKEN)
