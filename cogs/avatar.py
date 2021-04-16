import json
import os
import discord
from discord.ext import commands
from PIL import Image, ImageDraw
from io import BytesIO
from random import randint


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
        print(f'{number_of_pieces} pieces created')

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
# Helper Functions


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


def setup(client):  # Cog setup command
    client.add_cog(avatar(client))


'''
        destinations = [(0, 0), (0, 800), (800, 0), (800, 800)]
        for target in destinations:
            # Set image destinations
            step_count = 10
            for num in range(number_of_pieces):
                img_pieces[num].set_destination(target, step_count)
            # Move pieces
            for _ in range(step_count):
                temp = background.copy()
                for piece in img_pieces:
                    temp.paste(piece.pic, piece.next_location())
                frames.append(temp)
            # Set destinations back to original locations
            for num in range(number_of_pieces):
                img_pieces[num].set_destination(
                    img_pieces[num].origin, step_count)
            # Move pieces
            for _ in range(step_count):
                temp = background.copy()
                for piece in img_pieces:
                    temp.paste(piece.pic, piece.next_location())
                frames.append(temp)
'''
