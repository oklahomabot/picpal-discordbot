import os
import discord
import requests
import urllib.parse
from discord.ext import commands
from dotenv import load_dotenv
from random import randint
from PIL import Image, ImageDraw
from io import BytesIO


class images(commands.Cog):
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

    @commands.command(aliases=['toilet'], hidden=False)
    async def flush(self, ctx, *, user=None):
        '''
        Flush someone down the drain
        Returns gif image from mentioned user
        '''
        # Convert user to user or member / use author
        if user:
            try:
                user = await commands.converter.MemberConverter().convert(ctx, user)
            except:
                await ctx.send(f"I don\'t know {user}, lets just use your avatar ...")
                user = ctx.author
        else:
            user = ctx.author
        folder = os.path.join('./', 'cogs', 'gifs', 'flush')
        im = Image.open(os.path.join(folder, 'flush_master.png'))
        background = im.copy()
        background.putalpha(255)

        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar = im.copy()

        parameters = [(300, (100, 100), (50, 300)),
                      (0, (100, 100), (50, 300)),
                      (55, (100, 100), (50, 300)),
                      (110, (100, 100), (50, 300)),
                      (180, (100, 100), (80, 120)),
                      (250, (90, 90), (225, 20)),
                      (330, (85, 85), (400, 50)),
                      (0, (85, 85), (440, 150)),
                      (70, (80, 80), (360, 255)),
                      (140, (80, 80), (190, 215)),
                      (210, (70, 70), (225, 110)),
                      (280, (65, 65), (300, 110)),
                      (0, (60, 60), (380, 150)),
                      (60, (50, 50), (375, 165)),
                      (120, (40, 40), (380, 170)),
                      (180, (20, 20), (390, 180))]

        frames = []
        for rot, size, paste_loc in parameters:
            frames.append(paste_for_gif(background, avatar,
                                        rot=rot, size=size, paste_loc=paste_loc))
        frames.extend([background, background, background])

        # Assemble and publish animated gif
        out_file = os.path.join(folder, 'output.gif')
        frames[0].save(out_file, save_all=True, append_images=frames[1:],
                       optimize=True, duration=200, loop=0, interlace=True, disposal=2)
        await ctx.send(file=discord.File(out_file))

        return


def mask_circle(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    return im


def resize_avatar(avatar, size, rot=0, make_circle=True):
    new_avatar = avatar.copy()
    new_avatar = new_avatar.rotate(rot)
    new_avatar = new_avatar.resize(size)
    if make_circle:
        new_avatar = mask_circle(new_avatar)
    return new_avatar


def paste_for_gif(background, avatar, rot, size, paste_loc):
    ''' pastes image onto background image and returns image '''
    sized_avatar = resize_avatar(avatar, size, rot=rot)
    im = background.copy()
    im.alpha_composite(sized_avatar, dest=paste_loc)
    return im


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
    client.add_cog(images(client))
