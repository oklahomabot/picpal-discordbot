import os
import discord
import requests
import urllib.parse
import shutil
from discord.ext import commands
from dotenv import load_dotenv
from random import randint


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
        await ctx.send(f'Do not forget about karma {ctx.author.name} ...')

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

        await ctx.send(file=discord.File(out_path))


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


# get api token for image APIs
load_dotenv()
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')


def setup(client):  # Cog setup command
    client.add_cog(api_images(client))
