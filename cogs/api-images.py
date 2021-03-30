import os
from typing import Generator
import discord
import requests
import urllib.parse
import shutil
import json
from discord.ext import commands
from random import randint
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

# HELPER FUNCTIONS


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


def get_imgflip(template_id=112126428, text0='', text1=''):
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
    data_file = os.path.join('./', 'cogs\gifs\imgflip', 'imgfliptop100.txt')
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
    data_file = os.path.join('./', 'cogs\gifs\imgflip', 'imgfliptop100.txt')
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

    @commands.command(aliases=['pic', 'picture'], hidden=False)
    async def get_pic(self, ctx, *, search_txt=None):
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

    @commands.command(aliases=['ani'], hidden=False)
    async def animu(self, ctx, *, category=None):
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
            await ctx.send(('Please use meme name directly instead of \"make_meme\".') +
                           ('Use help make_meme for the full list of memes.'))
            return
        if (not message) or ('+' not in message):
            await ctx.send('Bad Input : ex) <template_name> text0+text1 (\"+\" seperates two text strings)')
            return

        text0 = message.split('+')[0]
        text1 = message.split('+')[1]

        template_id = find_imgflip_id_using_alias(ctx.invoked_with)

        url = get_imgflip(template_id, text0, text1)
        print(f'Command make_meme url={url}')
        if not url:
            await ctx.send(f"Something happened, I couldn\'t get your image {ctx.author.display_name} :(")
            return
        embed = discord.Embed(
            title='MEME Generator', description=f'{ctx.invoked_with}', timestamp=datetime.now(tz=timezone.utc))
        embed.set_image(url=get_imgflip(template_id, text0, text1))
        embed.set_thumbnail(url=self.client.user.avatar_url_as(size=64))
        embed.set_footer(
            text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(client):  # Cog setup command
    client.add_cog(api_images(client))
