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


class custom_images(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.command(aliases=['open_doors'], hidden=False)
    async def visitor(self, ctx, user=None):
        '''
        Look who's visiting ...
        Returns gif image using mentioned user
        '''

        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        sized_avatar = resize_avatar(avatar, (152, 152), rot=0)

        img_name = 'visitor'
        folder = os.path.join('./', 'cogs', 'gifs', img_name)
        whitepic = Image.open(os.path.join(folder, 'background.png'))
        whitepic.alpha_composite(sized_avatar, dest=(50, 60))

        frames = []
        for frame_num in range(17):
            background = whitepic.copy()
            frame_name = f'frame_{frame_num:02}.png'
            im = Image.open(os.path.join(folder, 'frames', frame_name))
            background.alpha_composite(im)
            frames.append(background)
        out_file = make_output(frames, 'visitor', speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['grow', 'sunflower'], hidden=False)
    async def flower(self, ctx, user=None):
        '''
        Grow a beautiful flower
        Returns gif image using mentioned user
        '''

        img_name = 'flower'
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        parameters = get_parameters(img_name)
        frames = construct_frames(parameters, avatar, img_name)
        out_file = make_output(frames, img_name, speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['slam_dunk', 'slamdunk'], hidden=False)
    async def dunk(self, ctx, user=None):
        '''
        Slam Dunk someone for fun
        Returns gif image using mentioned user
        '''

        img_name = 'dunk'
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        parameters = get_parameters(img_name)
        frames = construct_frames(parameters, avatar, img_name)
        out_file = make_output(frames, img_name, speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(hidden=False)
    async def flush(self, ctx, user=None):
        '''
        Flush someone down the drain
        Returns gif image using mentioned user
        '''
        img_name = 'flush'
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        parameters = get_parameters(img_name)
        frames = construct_frames(parameters, avatar, img_name)
        out_file = make_output(frames, img_name, speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['fly_high'], hidden=False)
    async def flying(self, ctx, user=None):
        '''
        Soaring through the air looks fun
        Returns gif image using mentioned user
        '''
        img_name = 'flying'
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        parameters = get_parameters(img_name)
        frames = construct_frames(parameters, avatar, img_name)
        out_file = make_output(frames, img_name, speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['rocket'], hidden=False)
    async def launch(self, ctx, user=None):
        '''
        Woosh goes the rocket!
        Returns gif image using mentioned user
        '''
        img_name = 'launch'
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        parameters = get_parameters(img_name)
        frames = construct_frames(parameters, avatar, img_name)
        out_file = make_output(frames, img_name, speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(hidden=False)
    async def pepe(self, ctx, user=None):
        '''
        Don't Stare at the frog too long
        Returns gif image using mentioned user
        '''
        img_name = 'pepe'
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        parameters = get_parameters(img_name)
        frames = construct_frames(parameters, avatar, img_name)
        out_file = make_output(frames, img_name, speed=get_speed(img_name))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['washer', 'clean'], hidden=False)
    async def wash(self, ctx, *, user=None):
        '''
        Clean yourself or your dirty friends
        Returns gif image using mentioned user
        '''

        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)

        sized_avatar = resize_avatar(avatar, (125, 125), rot=0)

        folder = os.path.join('./', 'cogs', 'gifs', 'wash')

        # sized to match washer images (335,371) pixels
        whitepic = Image.new('RGBA', (335, 371), (255, 255, 255, 255))

        # 16 images - avatar rotated each image
        frames = []
        rot = 360
        for _ in range(4):
            for frame_num in range(4):
                spin = -55 if frame_num in [0, 2] else 10
                rot += spin
                background = whitepic.copy()
                background.alpha_composite(
                    sized_avatar.rotate(rot), dest=(100, 150))
                frame_name = f'frame_{frame_num:02}.png'
                im = Image.open(os.path.join(folder, 'frames', frame_name))
                washer_img = im.copy()
                background.alpha_composite(washer_img)
                frames.append(background)

        out_file = make_output(frames, 'wash', speed=get_speed('wash'))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['BEER'], hidden=False)
    async def beer(self, ctx, *, user=None):
        '''
        Enjoy a brew with a friend
        Returns gif image using mentioned user
        '''
        # 2 avatar .... perhaps store both in json and split+optional 2nd list/avatar constructing frames
        user = await get_guild_member(ctx, user)
        avatar = await make_avatar(user)
        avatar_author = await make_avatar(ctx.author)

        par_user = get_parameters('beer')
        par_auth = get_parameters('beer', 'beer-author')

        folder = os.path.join('./', 'cogs', 'gifs', 'beer')
        frame_folder = os.path.join(folder, 'frames')
        frames = []
        for frame_name in os.listdir(frame_folder):
            if frame_name == 'backup_frames':
                continue

            frame_num = int(frame_name.split("_")[1][:2])
            im = Image.open(os.path.join(frame_folder, frame_name))
            background = im.copy()
            size_u = (par_user[frame_num][1][0], par_user[frame_num][1][1])
            loca_u = (par_user[frame_num][2][0], par_user[frame_num][2][1])
            size_a = (par_auth[frame_num][1][0], par_auth[frame_num][1][1])
            locu_a = (par_auth[frame_num][2][0], par_auth[frame_num][2][1])
            temp_img = (paste_for_gif(background, avatar,
                                      rot=par_user[frame_num][0], size=size_u,
                                      paste_loc=loca_u))
            frames.append(paste_for_gif(temp_img, avatar_author,
                                        rot=par_auth[frame_num][0], size=size_a,
                                        paste_loc=locu_a))

        # Assemble and publish animated gif
        out_file = make_output(frames, 'beer', speed=get_speed('beer'))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        return

    @commands.command(aliases=['ttt', 'tic_tac_toe'], hidden=False)
    async def tictactoe(self, ctx, *, user=None):
        '''
        A random tic tac toe game with anyone
        '''

        user = await get_guild_member(ctx, user)
        if ctx.author == user:
            text = (("How about you pretend to mention another user and I pretend to make your game?") +
                    (f"\nTry mentioning a member of {ctx.guild.name} ... or don\'t."))
            await ctx.send(text)
            return

        avatar = await make_avatar(user)
        avatar = resize_avatar(avatar, (150, 150), rot=0)
        avatar_author = await make_avatar(ctx.author)
        avatar_author = resize_avatar(avatar_author, (150, 150), rot=0)

        folder = os.path.join("./", "cogs", 'gifs', 'tictactoe')
        im = Image.open(os.path.join(folder, "blank_board.png"))
        background = im.copy()

        plays_first = randint(1, 2)  # author is player 1 or player 2
        avatars = []
        if plays_first == 1:
            avatars.extend([avatar_author, avatar])
        else:
            avatars.extend([avatar, avatar_author])

        paste_loc = [(40, 40), (230, 40), (420, 40), (40, 230), (230, 230),
                     (420, 230), (40, 420), (230, 420), (420, 420)]

        result, frames = random_tictactoe(avatars, background, paste_loc)

        if result == 'tie':
            output_text = 'No Winner, game is a tie'
        else:
            if (result == 1 and plays_first == 1) or (result == 2 and plays_first == 2):
                winner_name = ctx.author.display_name
            else:
                winner_name = user.display_name
            output_text = (f'{winner_name} is the winner!')

        out_file = os.path.join(folder, "output.gif")
        frames[0].save(out_file, save_all=True, append_images=frames[1:],
                       optimize=True, duration=1000, interlace=True, disposal=2)
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)
        await ctx.send(output_text)
        return

    @commands.command(aliases=['BRICK'], hidden=False)
    async def brick(self, ctx, *, user=None):
        '''
        Remove friend from the brick wall
        Returns gif image using mentioned user
        '''
        img_name = 'brick'
        victim = await get_guild_member(ctx, user)
        victim = await make_avatar(victim)
        victim = victim.resize((280, 80))
        author = await make_avatar(ctx.author)
        author = author.resize((128, 128))
        author = mask_circle(author)
        parameters = get_parameters(img_name)
        folder = os.path.join('./', 'cogs', 'gifs', img_name)
        frames = []
        for frame_num in range(len(parameters)):
            background = Image.open(os.path.join(
                folder, 'frames', (f'frame_{frame_num:02d}.png')))
            if frame_num <= 15:
                background.alpha_composite(victim, dest=(160, 73))
            rot = parameters[frame_num][0]
            size = (parameters[frame_num][1][0], parameters[frame_num][1][1])
            paste_loc = (parameters[frame_num][2][0],
                         parameters[frame_num][2][1])
            background = paste_for_gif(background, author, rot=rot,
                                       size=size, paste_loc=paste_loc)
            frames.append(background.copy())

        out_file = make_output(frames, 'brick', speed=get_speed('brick'))
        await ctx.send(file=discord.File(out_file))
        os.remove(out_file)


def mask_circle(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    return im


async def make_avatar(user):
    asset = user.avatar_url_as(static_format='png')
    data = BytesIO(await asset.read())
    im = Image.open(data)
    # avatar = im.copy()
    # avatar = make_RGBA(avatar)
    im = make_RGBA(im)
    return im


def resize_avatar(avatar, size, rot=0, make_circle=True):
    new_avatar = avatar.copy()
    new_avatar = new_avatar.rotate(rot)
    if size != new_avatar.size:
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


def get_parameters(img_name, filename=None):
    '''
    One Entry storage example (key is frame_number)
    [rotation, [sizeX,sizeY], [locationX,locationY]]
    [[0,[200,200],[100,100]]]
    '''
    filename = img_name if not filename else filename
    data_file = os.path.join('./', 'cogs', 'gifs',
                             img_name, f'{filename}.json')
    with open(data_file) as json_file:
        return_list = json.load(json_file)
    return return_list


def construct_frames(parameters, avatar, img_name):

    folder = os.path.join('./', 'cogs', 'gifs', img_name)
    frame_folder = os.path.join(folder, 'frames')
    frames = []
    for frame_num in range(len(parameters)):
        filename = f'frame_{frame_num:02d}.png'
        im = Image.open(os.path.join(frame_folder, filename))
        background = im.copy()
        rot = parameters[frame_num][0]
        size = (parameters[frame_num][1][0], parameters[frame_num][1][1])
        paste_loc = (parameters[frame_num][2][0], parameters[frame_num][2][1])
        background = paste_for_gif(background, avatar, rot=rot,
                                   size=size, paste_loc=paste_loc)
        frames.append(background)

    return frames


def make_output(frames, img_name, speed=100):
    folder = os.path.join('./', 'cogs', 'gifs', img_name)
    out_file = os.path.join(folder, 'output.gif')
    frames[0].save(out_file, save_all=True, append_images=frames[1:],
                   optimize=True, duration=speed, loop=0, interlace=True, disposal=2)
    return out_file


def make_RGBA(im):
    if im.mode == 'RGBA':
        return im
    im = im.convert('RGBA')
    im.putalpha(255)
    return im


def all_match(my_list, val):
    result = True if my_list.count(val) == len(my_list) else False
    return result


def tictactoe_winner(board):
    '''Returns False if no winner, tie or player_num'''
    lines = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 4, 7],
             [2, 5, 8], [3, 6, 9], [1, 5, 9], [3, 5, 7]]
    for player_num in [1, 2]:
        for line in lines:
            if all_match([board[line[0]-1], board[line[1]-1], board[line[2]-1]], player_num):
                return player_num

    # check for full tictactoe board
    return False if 0 in board else 'tie'


def tictactoe_string(board):
    temp = ''
    for row in range(3):
        for col in range(3):
            temp = temp+f'{board[row*3+col]}'
            if col == 2:
                temp = temp+'\n'
            else:
                temp = temp+'|'
    return temp


def random_tictactoe(avatars, background, paste_loc):
    board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    empty_spaces = [x+1 for x in range(9)]
    player_num = 1
    game_result = False
    img_frames = []
    tmp_img = background.copy()
    img_frames.append(tmp_img)
    while game_result == False:
        choice = empty_spaces.pop(randint(0, len(empty_spaces)-1))
        board[choice-1] = player_num
        background.alpha_composite(
            avatars[player_num-1], dest=paste_loc[choice-1])
        tmp_img = background.copy()
        img_frames.append(tmp_img)

        player_num = 1 if player_num == 2 else 2
        game_result = tictactoe_winner(board)

    return game_result, img_frames


def get_speed(img_name):
    speed_dic = {'flying': 40, 'pepe': 20, "dunk": 90, 'flush': 200,
                 'wash': 300, 'beer': 90, 'launch': 40, 'visitor': 200,
                 'brick': 100, 'flower': 100}
    return 200 if img_name not in speed_dic else speed_dic[img_name]


def setup(client):  # Cog setup command
    client.add_cog(custom_images(client))
