import os
import discord
import pymongo
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

mongo_pass = os.getenv('MONGO_PASS')
db_name = 'picpal'
temp = ((f"mongodb+srv://picpal_bot:{mongo_pass}@picpal.khorx.mongodb.net") +
        (f"/{db_name}?retryWrites=true&w=majority"))
mongo_client = pymongo.MongoClient(temp)
db = mongo_client[db_name]
# print(f'Mongo db {db_name} tables: {db.list_collection_names()}')


class leveling(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.Cog.listener("on_message")
    async def message_xp(self, message):
        if message.author.bot:
            return
        if not is_leveling_on(message.guild.id, message.guild.name):
            return
        promoted = add_exp(message.guild.id, message.author.id,
                           message.author.display_name)
        if promoted:
            await message.channel.send(f'User {message.author.display_name} promoted to level {promoted}')

    @commands.command(aliases=['edit_leveling'], hidden=False)
    async def leveling(self, ctx, command=None):
        ''' Turn leveling on/off for your server '''
        ''' on/off/true/false can be used '''

        guild_record = get_guild_document(ctx.guild.id)
        temp = ((f'Leveling is currently set to {guild_record["leveling_on"]}\n') +
                (f'Type \"{self.client.command_prefix}leveling \" + ') +
                (f'on, off, true or false to change this setting'))
        if not command:
            await ctx.send(temp)
            return

        command = command.lower()
        if command not in ['on', 'off', 'true', 'false']:
            await ctx.send(temp)
            return

        value = True if command in ['on', 'true'] else False
        db.guilds.update({'guild_id': ctx.guild.id}, {
                         '$set': {'leveling_on': value}})
        await ctx.send(f'Leveling has been set to **{command}** for this server {ctx.author.display_name}')
        return

    @commands.command(aliases=['user_level', 'userlevel', 'experience', 'xp'], hidden=False)
    async def level(self, ctx, *, user=None):
        ''' Returns User Experience Level '''
        ''' Mention someone or look up your own info '''
        # Find level and next level and ratio
        # Output embed or just text message
        user = await get_guild_member(ctx, user)
        user_info = get_user_document(ctx.guild.id, user.id)
        if not user_info:
            user_info = make_new_user_record(
                ctx.guild.id, user.id, user.display_name)
        level = user_info['level']
        base_xp = level_start_xp(level)
        next_xp = level_start_xp(level+1)
        progress = (user_info['xp']-base_xp)/(next_xp-base_xp)
        text = ((f"Currently level **{level}** with **{user_info['xp']}** XP\n") +
                (f"[**{level:02d}|**{text_progress_bar(progress, chr(9632), chr(9633))}**|{level+1:02d}**]") +
                (f"(https://www.youtube.com/watch?v=QB7ACr7pUuE) **{int(progress*100):02d}%**"))

        embed = discord.Embed(title=(f"{user.display_name}\'s XP ({ctx.guild.name})"),
                              description=text, colour=discord.Colour.blurple(),
                              timestamp=datetime.utcnow())
        embed.set_thumbnail(url=user.avatar_url_as(size=64))
        embed.set_footer(
            text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)


def is_leveling_on(guild_id, guild_name):
    query = {'guild_id': guild_id}
    record = db.guilds.find_one(query)
    if not record:  # Add guild to tbl_guilds
        record = make_new_guild_record(guild_id, guild_name)
    return record['leveling_on']


def make_new_guild_record(id, name):
    query = {'guild_id': id}
    record = db.guilds.find_one(query)
    if not record:  # Add new guild to tbl_guilds
        record = {'guild_id': id, 'guild_name': name,
                  'leveling_on': False}
        db.guilds.insert_one(record)
        print(f'Cog Leveling: added guild {name} to guilds table')
    return record


def make_new_user_record(guild_id, user_id, user_name):
    query = {'guild_id': guild_id, 'user_id': user_id}
    record = db.levels.find_one(query)
    if not record:  # Make new user to tbl_levels
        record = {'guild_id': guild_id,
                  'user_id': user_id, 'name': user_name, 'xp': 0, 'level': 0}
        db.levels.insert_one(record)
        print(
            f'Cog Leveling:Added new guild_id/user_id {guild_id}/{user_id}to tbl_levels')
    return record


def add_exp(guild_id, user_id, user_name):
    new_level = False
    query = {'guild_id': guild_id, 'user_id': user_id}
    record = db.levels.find_one(query)
    if not record:  # Make new user to tbl_levels
        record = make_new_user_record(guild_id, user_id, user_name)
    record['xp'] += 5
    if find_level(record['xp']) != record['level']:
        new_level = find_level(record['xp'])
        record['level'] = new_level
    record['name'] = user_name  # Ensures current Member.display_name stored
    db.levels.replace_one(query, record)

    return new_level


def get_guild_document(guild_id):
    ''' None returned if non existent '''
    query = {'guild_id': guild_id}
    record = db.guilds.find_one(query)
    return record


def get_user_document(guild_id, user_id):
    ''' None returned if non existent '''
    query = {'guild_id': guild_id, 'user_id': user_id}
    record = db.levels.find_one(query)
    return record


def replace_user_document(record):
    query = {'guild_id': record["guild_id"], 'user_id': record["user_id"]}
    db.levels.replace_one(query, record)


def change_user_name(guild_id, user_id, name):
    query = {'guild_id': guild_id, 'user_id': user_id}
    replace = {'$set': {'name': name}}
    db.levels.update(query, replace)


def text_progress_bar(ratio, chr1, chr2):
    temp = ''
    for section in range(1, 11):
        to_add = chr1 if (ratio*100)//10 >= section else chr2
        temp = temp+to_add
    return temp


async def get_guild_member(ctx, user=None):
    try:
        user = await commands.converter.MemberConverter().convert(ctx, user)
    except:
        user = ctx.author
    return user


def find_level(xp):
    return int(xp**(1/4))


def level_start_xp(level):
    return level**4


def setup(client):  # Cog setup command
    client.add_cog(leveling(client))
