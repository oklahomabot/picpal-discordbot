import os
import discord
import aiohttp
import random
from discord.ext import commands
from PIL import Image, ImageDraw
from io import BytesIO
from functools import partial


class ImgPiece():
    def __init__(self, piece_num, pic, origin, destination=None):
        self.piece_num = piece_num
        self.pic = pic
        self.origin = origin
        self.x = origin[0]
        self.y = origin[1]
        self.pos_num = 0
        self.locations = []
        if not destination:
            self.destination = origin

    def next_location(self):
        self.pos_num += 1
        next = self.locations[self.pos_num]
        self.x = next[0]
        self.y = next[1]
        return next

    def set_destination(self, destination, steps):
        self.pos_num = 0
        loc_list = []
        loc_list.append((self.x, self.y))
        x = self.x
        y = self.y
        x_step_size = ((destination[0]-x)/steps)
        y_step_size = ((destination[1]-y)/steps)
        for _ in range(steps-1):
            x += x_step_size
            y += y_step_size
            loc_list.append((int(x), int(y)))
        loc_list.append(destination)
        self.locations = loc_list
        return


class avatar(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser
        # create a ClientSession
        self.session = aiohttp.ClientSession(loop=client.loop)

    @staticmethod
    def make_pat_gif(avatar):
        folder = os.path.join('./', 'cogs', 'gifs', 'pat')
        sizex, sizey = 112, 112
        avatar_sizes = [(90, 70), (90, 70), (95, 60), (97, 55),
                        (100, 50), (97, 55), (95, 60), (90, 70)]
        background = Image.open(os.path.join(folder, 'background.png'))
        frames = []
        for img_num in range(8):
            frame = background.copy()
            av = avatar.resize(avatar_sizes[img_num])
            av_width = avatar_sizes[img_num][0]
            av_height = avatar_sizes[img_num][1]
            hand = Image.open(os.path.join(
                folder, 'hands', f'{str(img_num)}.png'))
            frame.alpha_composite(
                av, dest=((sizex-av_width)//2, sizey-av_height))
            frame.alpha_composite(hand, dest=((0, int(1.5*(70-av_height)))))
            frames.append(frame)
        outfile = os.path.join(folder, 'output.gif')
        frames[0].save(outfile, 'GIF', disposal=2, transparency=0, save_all=True,
                       append_images=frames[1:], optimize=False, duration=12, loop=0)
        return outfile

    @commands.command(aliases=['pet_pat'], hidden=False)
    async def pat(self, ctx, *, user=None):
        '''
        Good Boy ...
        Returns gif image using mentioned user
        '''

        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)

        # create partial function so we don't have to stack the args in run_in_executor
        fn = partial(self.make_pat_gif, avatar)
        outfile = await self.client.loop.run_in_executor(None, fn)
        self.session.close()
        await ctx.send(file=discord.File(outfile))
        os.remove(outfile)

    @commands.command(aliases=['splode'], hidden=False)
    async def explode(self, ctx, *, user=None):
        '''
        What is happening??????
        Returns gif image using mentioned user
        '''

        command_name = 'avatar'

        user = await get_guild_member(ctx, user)
        # make avatar image
        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        im = im.resize((500, 500), Image.ANTIALIAS)
        avatar = im.copy()

        # make individual piece objects
        background_border = 200
        img_pieces = []
        for row in range(5):
            for col in range(5):
                x = row*100
                y = col*100
                piece_num = row*5+col
                temp = ImgPiece(piece_num, avatar.crop(
                    (x, y, x+100, y+100)), (x+background_border, y+background_border))
                img_pieces.append(temp)

        number_of_pieces = len(img_pieces)
        # print(f'{number_of_pieces} pieces created')

        folder = os.path.join('./', 'cogs', 'gifs', command_name)
        background = Image.open(os.path.join(folder, 'background.png'))

        # First frame centered
        temp = background.copy()
        temp.paste(avatar, (200, 200))
        frames = []
        for _ in range(15):
            frames.append(temp)

        for _ in range(4):
            # left
            temp = background.copy()
            temp.paste(avatar, (175, 200))
            frames.append(temp)
            # right
            temp = background.copy()
            temp.paste(avatar, (225, 200))
            frames.append(temp)

        # centered
        temp = background.copy()
        temp.paste(avatar, (200, 200))
        frames.append(temp)

        # Explode
        steps = 10
        # Write these to a json file to save space?
        destinations = get_outer_destinations()
        for index, piece in enumerate(img_pieces):
            piece.set_destination(destinations[index], steps)

        # Move pieces
        for _ in range(steps):
            temp = background.copy()
            for piece in img_pieces:
                temp.paste(piece.pic, piece.next_location())
            frames.append(temp)
        # Set destinations back to original locations
        for num in range(number_of_pieces):
            img_pieces[num].set_destination(
                img_pieces[num].origin, steps)
        # Move pieces
        for _ in range(steps):
            temp = background.copy()
            for piece in img_pieces:
                temp.paste(piece.pic, piece.next_location())
            frames.append(temp)

        outfile = os.path.join(folder, (f'{ctx.author}.gif'))
        frames[0].save(outfile, save_all=True, append_images=frames[1:],
                       optimize=True, duration=60, loop=0, interlace=True, disposal=2)
        await ctx.send(file=discord.File(outfile))
        os.remove(outfile)
        return

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
            embed = discord.Embed(title='Avatar', colour=discord.Colour.blue())
            embed.set_image(url=member.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Avatar', colour=discord.Colour.blue())
            embed.set_image(url=member.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['goal'], hidden=False)
    async def escape(self, ctx, *, user=None):
        '''
        Feeling lucky? You get 20 moves to reach the goal.
        Randomly moves you or a friend you mention
        Returns gif image
        '''

        user = await get_guild_member(ctx, user)
        # make avatar image
        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        im = im.resize((500, 500), Image.ANTIALIAS)
        avatar = im.copy()

        # make individual piece objects
        background_border = 200
        img_pieces = []
        for row in range(5):
            for col in range(5):
                x = row*100
                y = col*100
                piece_num = row*5+col
                temp = ImgPiece(piece_num, avatar.crop(
                    (x, y, x+100, y+100)), (x+background_border, y+background_border))
                img_pieces.append(temp)

        folder = os.path.join('./', 'cogs', 'gifs', 'escape')
        background = Image.open(os.path.join(folder, 'back_goal.png'))

        # First frame centered
        temp = background.copy()
        temp.paste(avatar, (200, 200))
        frames = []
        for _ in range(10):
            frames.append(temp)

        # shrink to one piece in middle
        steps = 5
        for piece in img_pieces:
            piece.set_destination((400, 400), steps)
        # Move pieces
        for _ in range(steps):
            temp = background.copy()
            for piece in img_pieces:
                temp.paste(piece.pic, piece.next_location())
            frames.append(temp)

        # Move image randomly around frame
        small_avatar = avatar.resize((100, 100), Image.ANTIALIAS)
        path_block = Image.new('RGB', (100, 100), (245, 216, 137))
        current_location = (400, 400)
        temp = background.copy()
        winner = False
        move_num = 0
        while move_num < 20 and not winner:
            move_num += 1
            temp.paste(path_block, current_location)
            current_location = get_random_adjacent_grid(current_location)
            temp.paste(small_avatar, current_location)
            frames.append(temp.copy())
            winner = True if ((current_location[0] in [0, 800]) or
                              (current_location[1] in [0, 800])) else False

        banner_fn = 'back_winner_900x200.png' if winner else 'back_loser_900x200.png'
        avatar = avatar.resize((200, 200), Image.ANTIALIAS)
        avatar = mask_circle(avatar)
        banner = Image.open(os.path.join(folder, banner_fn))
        if winner:
            banner.paste(avatar, (0, 0))
            banner.paste(avatar, (700, 0))
        where = (0, 700) if current_location[1] < 500 else (0, 0)
        temp.paste(banner, where)
        frames.append(temp)

        outfile = os.path.join(folder, (f'{ctx.author}.gif'))
        frames[0].save(outfile, save_all=True, append_images=frames[1:],
                       optimize=True, duration=200, interlace=True, disposal=2)
        await ctx.send(file=discord.File(outfile))
        os.remove(outfile)
        return

# Helper Functions


def make_RGBA(im):
    if im.mode == 'RGBA':
        return im
    im = im.convert('RGBA')
    im.putalpha(255)
    return im


async def make_avatar(user):
    asset = user.avatar_url_as(static_format='png')
    data = BytesIO(await asset.read())
    im = Image.open(data)
    im = make_RGBA(im)
    return im


def mask_circle(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    return im


def get_outer_destinations():
    destinations = []
    destinations.append((000, 000))
    destinations.append((200, 800))
    destinations.append((400, 000))
    destinations.append((600, 800))
    destinations.append((800, 000))

    destinations.append((800, 200))
    destinations.append((500, 800))
    destinations.append((100, 800))
    destinations.append((000, 500))
    destinations.append((000, 200))

    destinations.append((000, 400))
    destinations.append((000, 100))
    destinations.append((300, 000))
    destinations.append((700, 000))
    destinations.append((000, 800))

    destinations.append((800, 600))
    destinations.append((800, 100))
    destinations.append((500, 000))
    destinations.append((800, 700))
    destinations.append((000, 600))

    destinations.append((000, 800))
    destinations.append((200, 000))
    destinations.append((400, 800))
    destinations.append((600, 000))
    destinations.append((800, 800))
    return destinations


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


def get_random_adjacent_grid(location):
    # based on 900x900 frame and piece size of 100,100
    available = []
    if location[0] > 0:
        available.append((-100, 0))
    if location[0] < 800:
        available.append((100, 0))
    if location[1] > 0:
        available.append((0, -100))
    if location[1] < 800:
        available.append((0, 100))

    adjust = random.choice(available)
    new_location = (location[0]+adjust[0], location[1]+adjust[1])

    return new_location


def setup(client):  # Cog setup command
    client.add_cog(avatar(client))
