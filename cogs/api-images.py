import os
from typing import Generator
import discord
import requests
import urllib.parse
import shutil
import json
import asyncio
from discord.ext import commands
from random import randint
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

# HELPER FUNCTIONS


def replace_imgflip_dic(my_dic):
    data_path = os.path.join('./', 'cogs', 'gifs',
                             'imgflip', 'imgfliptop100.txt')

    with open(data_path, 'w+') as outfile:
        json.dump(my_dic, outfile)
    return


def extend_unique_items(old_list, additional_items):
    new_list = old_list.copy()
    for item in additional_items:
        if item not in new_list:
            new_list.append(item)

    return new_list


async def get_guild_member(ctx, user=None):
    # Convert user to user or member / use author
    if user:
        try:
            user = await commands.converter.MemberConverter().convert(ctx, user)
        except:
            await ctx.send(f"I don\'t know {user}, lets just use your avatar ...")
            user = ctx.author
    else:
        user = ctx.author
    return user


async def pixabay_url_search(ctx, search_by=None):
    '''
    Uses Pixabay's API to search for a pic url based on search_by
    If None given a random one will be supplied
    '''
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
    if search_by:
        getVars = {'key': PIXABAY_API_KEY,
                   'q': search_by, 'safesearch': 'true', 'page': 1}
    else:
        getVars = {'key': PIXABAY_API_KEY, 'safesearch': 'true', 'page': 1}

    url = 'https://pixabay.com/api/?'
    response = requests.get(url + urllib.parse.urlencode(getVars))

    if response.status_code == 200:
        data = response.json()
        if len(data['hits']) > 0:
            rndpic = randint(0, len(data['hits'])-1)
            return data['hits'][rndpic]['webformatURL']
        else:
            return ('https://cdn.dribbble.com/users/283708/screenshots/7084432/media/451d27c21601d96114f0eea20d9707e2.png?compress=1&resize=400x300')


def get_imgflip_url(template_id=112126428, text0='', text1=''):
    result_url = None
    username = os.getenv('IMGFLIP_USER')
    password = os.getenv('IMGFLIP_PASS')
    url = f'https://api.imgflip.com/caption_image'
    params = {
        'username': username,
        'password': password,
        'template_id': template_id,
        'text0': text0,
        'text1': text1
    }
    response = requests.request('POST', url, params=params).json()
    try:
        result_url = response['data']['url']
    except:
        result_url = None
    return result_url


def get_imgflip_dic():
    '''
    One Entry storage example (key is memeid extracted from https://imgflip.com/popular_meme_ids)
    {'112126428':{'rank': 1, 'full_name': 'Distracted Boyfriend',
                  'description': 'distracted bf, guy checking out another girl' 
                  'aliases': ['DistractedBoyfriend']}}
    '''
    data_file = os.path.join('./', 'cogs', 'gifs',
                             'imgflip', 'imgfliptop100.txt')
    with open(data_file) as json_file:
        return_dic = json.load(json_file)
    return return_dic


def save_imgflip_aliases(template_id, alias_list):
    '''Save Edited Aliases Back To DataFile'''
    if len(alias_list) == 0:
        print(
            f'COG api-images save_imgflip_aliases : Saving empty aliases list for {template_id}')
    temp_dic = get_imgflip_dic()
    temp_dic[str(template_id)]['aliases'] = alias_list
    data_file = os.path.join('./', 'cogs', 'gifs',
                             'imgflip', 'imgfliptop100.txt')
    with open(data_file, 'w+') as outfile:
        json.dump(temp_dic, outfile)
    return


def find_imgflip_id_using_alias(alias):

    temp_dic = get_imgflip_dic()
    for id in temp_dic.keys():
        if alias in temp_dic[id]['aliases']:
            return id
    return None


def get_meme_aliases():
    return_list = []
    temp_dic = get_imgflip_dic()
    for id in temp_dic.keys():
        for alias in temp_dic[id]['aliases']:
            return_list.append(alias)
    return return_list


class api_images(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.command(aliases=['get_pic', 'picture'], hidden=False)
    async def pic(self, ctx, *, search_txt=None):
        '''
        Provides an image using your search words (optional)
        Pictures retrieved using Pixabay's API
        '''
        if search_txt:
            embed = discord.Embed(title=f":mag: **{search_txt}** :mag:", colour=discord.Colour(
                0xE5E242), description=f"image provided by [Pixabay.com\'s API](https://pixabay.com/)")
        else:
            embed = discord.Embed(title=f"RANDOM PICTURE ... Good Luck :smile:", colour=discord.Colour(
                0xE5E242), description=f"image provided by [Pixabay.com\'s API](https://pixabay.com/)")

        result_link = await pixabay_url_search(ctx, search_txt)

        embed.set_image(url=result_link)
        embed.set_thumbnail(
            url=self.client.user.avatar_url_as(size=64))
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases=['giphy', 'gif_search'], hidden=False)
    async def gif(self, ctx, *, search_txt=None):
        '''
        Provides an image using your search words (optional)
        Pictures retrieved using giphy.com's API
        '''
        GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')
        getVars = {'api_key': GIPHY_API_KEY,
                   'tag': search_txt, 'rating': 'pg13'}
        url = 'https://api.giphy.com/v1/gifs/random?'
        response = requests.get(url + urllib.parse.urlencode(getVars))

        if response.status_code != 200:
            await ctx.send('Well ... that did not work for some reason.')
            return
        data = json.loads(response.text)
        title = 'RANDOM gif' if not search_txt else (f'\"{search_txt}\" GIF')
        embed = discord.Embed(
            title=title, colour=discord.Colour(0xE5E242),
            description=f"{data['data']['title']} [Powered By GIPHY](https://giphy.com/)",
            timestamp=datetime.now(tz=timezone.utc))
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        embed.set_footer(
            text=f'Requested by: {ctx.author.name}', icon_url=self.client.user.avatar_url)

        embed.set_image(url=data['data']['images']['original']['url'])
        await ctx.send(embed=embed)

        return

    @commands.command(aliases=['Trigger', 'TRIGGER'], hidden=False)
    async def trigger(self, ctx, *, user=None):
        '''
        Trigger someone, it is fun!
        This command uses some-random-API interface to retrieve image
        '''

        user = await get_guild_member(ctx, user)

        getVars = {'avatar': user.avatar_url_as(format='png')}
        url = f'https://some-random-api.ml/canvas/triggered/?'
        response = requests.get(
            url + urllib.parse.urlencode(getVars), stream=True)

        if response.status_code != 200:
            await ctx.send('Well ... that did not work for some reason.')
            return
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        response.raw.decode_content = True
        out_path = os.path.join('./', 'cogs', 'gifs',
                                'somerandomAPI', (f'output.gif'))
        with open(out_path, 'wb+') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        await ctx.send(f'Do not forget about karma {ctx.author.name} ...', file=discord.File(out_path))

    @commands.command(aliases=['animu'], hidden=False)
    async def ani(self, ctx, *, category=None):
        '''View an animu in category wink, hug, pat or face-palm'''

        if category == 'face palm':
            category = 'face-palm'

        valid_cats = ['wink', 'hug', 'pat', 'face-palm']
        if category not in valid_cats:
            text = f'Please try again selecting a category ex) \"{self.client.command_prefix}animu hug\"\n'
            text = text + 'Valid categories are **'
            text = text + \
                "** , **".join(valid_cats[:-1]) + f' and {valid_cats[-1]}**'
            await ctx.send(text)
            return

        url = f'https://some-random-api.ml/animu/{category}'
        response = requests.get(url)

        if response.status_code != 200:
            await ctx.send(f"Something happened, I couldn\'t get your image {ctx.author.display_name} :(")
            return

        embed = discord.Embed(
            title=f"**{category}** Animu Image", colour=discord.Colour(0xE5E242),
            description=f"image provided by [some-random-API.ml](https://some-random-API.ml/)",
            timestamp=datetime.now(tz=timezone.utc))
        embed.set_image(url=response.json()['link'])
        embed.set_thumbnail(url=self.client.user.avatar_url_as(size=64))
        embed.set_footer(
            text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=get_meme_aliases(), hidden=False)
    async def make_meme(self, ctx, *, message=None):
        '''Let's Make a Meme'''
        if ctx.invoked_with == 'make_meme':
            await ctx.send(('Please use a command directly instead of \"make_meme\"\n') +
                           (f'\"{self.client.command_prefix}meme_list\" to see all meme commands'))
            return
        if (not message):
            temp = ((f'Please add text field(s) and try again.\n') +
                    (f'ex) {self.client.command_prefix}changemymind text1+text2 ') +
                    (f'(\"+\" seperates the two text strings) The second text is optional'))
            await ctx.send(temp)
            return

        text0 = message.split('+')[0]
        if '+' in message:
            text1 = message.split('+')[1]
        else:
            text1 = ''

        template_id = find_imgflip_id_using_alias(ctx.invoked_with)

        url = get_imgflip_url(template_id, text0, text1)

        if not url:
            await ctx.send(f"Something happened, I couldn\'t get your image {ctx.author.display_name} :(")
            return
        embed = discord.Embed(title=f"{ctx.author.display_name}\'s MEME",
                              description=f"provided by [imgflip.com\'s API](https://imgflip.com/)",
                              colour=discord.Colour.blue())
        embed.set_image(url=url)
        embed.set_thumbnail(url=ctx.author.avatar_url_as(size=64))
        embed.set_footer(text=f'Type \"{self.client.command_prefix}meme_list\" for available memes',
                         icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['memes_list', 'list_memes', 'memeslist', 'listmemes', 'memelist'])
    async def meme_list(self, ctx, fields_per_page: int = 5):
        '''List of Meme Making Commands (from imgflip top100)'''
        if fields_per_page not in [3, 4, 5, 6, 7, 8, 9, 10]:
            await(ctx.send('fields_per_page set to 5 (must be 3-10)'))
            fields_per_page = 5

        imgflip_dic = get_imgflip_dic()

        title = 'MEME GENERATOR COMMANDS'
        description = '[List of Top 100 imgflip memes](https://imgflip.com/popular_meme_ids)'

        total_pages = len(imgflip_dic)//fields_per_page
        if len(imgflip_dic) % fields_per_page != 0:
            total_pages += 1

        embed_list = []
        for _ in range(total_pages):
            embed = discord.Embed(title=title, description=description,
                                  colour=discord.Colour.blue())
            embed.set_thumbnail(url=self.client.user.avatar_url_as(size=64))
            embed.set_footer(text=((f'Make meme by typing \"{self.client.command_prefix}') +
                                   ('<command> <text1>+<text2>\"')), icon_url=ctx.author.avatar_url)
            embed_list.append(embed)

        for index, meme in enumerate(imgflip_dic.keys()):
            temp_str = ' '.join(imgflip_dic[meme]['aliases'])
            embed_list[index //
                       fields_per_page].add_field(name=f'#{imgflip_dic[meme]["rank"]} '+imgflip_dic[meme]['full_name'], value=temp_str, inline=False)

        current = 1
        message = await ctx.send(f"Page {current}/{total_pages}", embed=embed_list[current-1])

        emoji_dic = {"⏪": -1*(total_pages+2)//4, "◀️": -1, "▶️": 1,
                     "⏩": (total_pages+2)//4, "⏹️": 0}
        for emoji in emoji_dic.keys():
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emoji_dic
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)
            except:
                return  # Exit Function (Timed Out) due to timeout error

            if str(reaction.emoji) == "⏹️":
                await message.edit(content='Process Stopped! Deleting Message', embed=None)
                await asyncio.sleep(3)
                await message.delete()
                await ctx.message.delete()
                return

            current += emoji_dic[str(reaction.emoji)]
            current = 1 if current < 1 else total_pages if current > total_pages else current
            await message.edit(content=f"Page {current} of {total_pages}", embed=embed_list[current-1])
            await message.remove_reaction(reaction, user)

    @commands.command(aliases=['add_meme_command', 'add_command', 'add_cmd', 'addcmd',
                               'del_meme_command', 'del_command', 'del_cmd', 'delcmd'], hidden=False)
    async def edit_meme_commands(self, ctx, meme_cmd, *, message=None):
        '''
        (Owner Only Function) edits make_meme function command aliases
        del_cmd <command> will remove one command alias
        add_cmd <command> <list> will add aliases
        adding uses a comma seperated list (no brackets needed)
        '''

        my_info = await self.client.application_info()
        if ctx.author != my_info.owner:
            await ctx.send('NO :smile:')
            return

        template_id = find_imgflip_id_using_alias(meme_cmd)
        if not template_id:
            await ctx.send(f'Nothing Done, failed to find {meme_cmd}')
            return

        my_dic = get_imgflip_dic()
        old_aliases = my_dic[template_id]['aliases']
        new_aliases = old_aliases.copy()

        if ctx.invoked_with[:3] == 'del':
            if len(old_aliases) < 2:
                await ctx.send('This meme must have at least one command.')
            else:
                new_aliases.remove(meme_cmd)
                my_dic[template_id]['aliases'] = new_aliases
        else:
            if not message:
                await ctx.send((f'Current commands to invoke {meme_cmd}: {old_aliases}\n') +
                               (f'Website description: {my_dic[template_id]["description"]}'))
                return

            extend_list = message.split(',')
            new_aliases = extend_unique_items(old_aliases, extend_list)

        my_dic[template_id]['aliases'] = new_aliases
        replace_imgflip_dic(my_dic)
        temp = ((f"Original Commands: {old_aliases}\n Edited   Commands: {new_aliases}\n") +
                ('Changes in command list will not be effective until next bot restart'))
        await ctx.send(temp)
        return


def setup(client):  # Cog setup command
    client.add_cog(api_images(client))
