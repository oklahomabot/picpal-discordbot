import os
import discord
from discord.ext import commands
from PIL import Image, ImageDraw
from io import BytesIO
from random import randint


class custom_images(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.command(aliases=['toilet'], hidden=False)
    async def flush(self, ctx, *, user=None):
        '''
        Flush someone down the drain
        Returns gif image using mentioned user
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
        avatar = make_RGBA(avatar)

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

    @commands.command(aliases=['DUNK'], hidden=False)
    async def dunk(self, ctx, *, user=None):
        '''
        Play basketball with a friend
        Returns gif image using mentioned user
        '''

        user = await get_guild_member(ctx, user)

        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar = im.copy()
        avatar = make_RGBA(avatar)

        parameters = dunk_paste_info()
        folder = os.path.join('./', 'cogs', 'gifs', 'dunk')
        frame_folder = os.path.join(folder, 'frames')
        frames = []
        for frame_name in os.listdir(frame_folder):
            if frame_name == 'backup_frames':
                continue

            frame_num = int(frame_name.split("_")[1][:2])
            im = Image.open(os.path.join(frame_folder, frame_name))
            background = im.copy()
            frames.append(paste_for_gif(background, avatar,
                                        rot=parameters[frame_num][0], size=parameters[frame_num][1],
                                        paste_loc=parameters[frame_num][2]))

        # Assemble and publish animated gif
        out_file = os.path.join(folder, 'output.gif')
        frames[0].save(out_file, save_all=True, append_images=frames[1:],
                       optimize=True, duration=90, loop=0, interlace=True, disposal=2)
        await ctx.send(file=discord.File(out_file))

        return

    @commands.command(aliases=['BEER'], hidden=False)
    async def beer(self, ctx, *, user=None):
        '''
        Enjoy a brew with a friend
        Returns gif image using mentioned user
        '''

        user = await get_guild_member(ctx, user)

        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar = im.copy()
        avatar = make_RGBA(avatar)

        asset = ctx.author.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar_author = im.copy()
        avatar_author = make_RGBA(avatar_author)

        parameters = []
        parameters_author = []
        for _ in range(5):
            parameters.append((10, (120, 120), (302, 170)))
            parameters_author.append((350, (120, 120), (85, 170)))

        parameters[1] = (10, (120, 120), (293, 170))
        parameters[2] = (10, (120, 120), (282, 170))
        parameters[3] = (10, (120, 120), (282, 170))
        parameters[4] = (10, (120, 120), (294, 170))

        parameters_author[1] = ((350, (120, 120), (89, 170)))
        parameters_author[2] = ((350, (120, 120), (100, 170)))
        parameters_author[3] = ((350, (120, 120), (100, 170)))
        parameters_author[4] = ((350, (120, 120), (89, 170)))

        folder = os.path.join('./', 'cogs', 'gifs', 'beer')
        frame_folder = os.path.join(folder, 'frames')
        frames = []
        for frame_name in os.listdir(frame_folder):
            if frame_name == 'backup_frames':
                continue

            frame_num = int(frame_name.split("_")[1][:2])
            im = Image.open(os.path.join(frame_folder, frame_name))
            background = im.copy()
            temp_img = (paste_for_gif(background, avatar,
                                      rot=parameters[frame_num][0], size=parameters[frame_num][1],
                                      paste_loc=parameters[frame_num][2]))
            frames.append(paste_for_gif(temp_img, avatar_author,
                                        rot=parameters_author[frame_num][0], size=parameters_author[frame_num][1],
                                        paste_loc=parameters_author[frame_num][2]))

        # Assemble and publish animated gif
        out_file = os.path.join(folder, 'output.gif')
        frames[0].save(out_file, save_all=True, append_images=frames[1:],
                       optimize=True, duration=90, loop=0, interlace=True, disposal=2)
        await ctx.send(file=discord.File(out_file))

        return

    @commands.command(aliases=['washer', 'clean'], hidden=False)
    async def wash(self, ctx, *, user=None):
        '''
        Clean yourself or your dirty friends
        Returns gif image using mentioned user
        '''

        user = await get_guild_member(ctx, user)

        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar = im.copy()
        avatar = make_RGBA(avatar)

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
                frame_name = f'tframe_{frame_num:02}.png'
                im = Image.open(os.path.join(folder, 'frames', frame_name))
                washer_img = im.copy()
                background.alpha_composite(washer_img)
                frames.append(background.copy())

        out_file = os.path.join(folder, 'output.gif')
        frames[0].save(out_file, save_all=True, append_images=frames[1:],
                       optimize=True, duration=300, loop=0, interlace=True, disposal=2)
        await ctx.send(file=discord.File(out_file))

        return

    @commands.command(aliases=['ttt', 'tic_tac_toe'], hidden=False)
    async def tictactoe(self, ctx, *, user=None):
        '''
        Generates a radom game of Tic Tac Toe with whomever you want
        '''

        try:
            user = await commands.converter.MemberConverter().convert(ctx, user)
        except:
            text = (("How about you pretend to mention another user and I pretend to make your game?") +
                    (f"\nTry mentioning a member of {ctx.guild.name} ... or don\'t."))
            await ctx.send(text)
            return

        asset = user.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar = im.copy()
        avatar = make_RGBA(avatar)
        avatar = resize_avatar(avatar, (150, 150), rot=0)

        asset = ctx.author.avatar_url_as(static_format='png')
        data = BytesIO(await asset.read())
        im = Image.open(data)
        avatar_author = im.copy()
        avatar_author = make_RGBA(avatar_author)
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

        result, final_board, frames = random_tictactoe(
            avatars, background, paste_loc)

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

        await ctx.send(output_text)

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


def dunk_paste_info():
    return_list = []
    return_list.append((0, (50, 50), (199, 150)))
    return_list.append((0, (50, 50), (199, 170)))
    return_list.append((0, (50, 50), (199, 191)))
    return_list.append((0, (50, 50), (199, 236)))
    return_list.append((0, (50, 50), (199, 211)))
    return_list.append((0, (50, 50), (199, 178)))
    return_list.append((0, (50, 50), (199, 152)))
    return_list.append((0, (50, 50), (199, 170)))
    return_list.append((0, (50, 50), (199, 211)))
    return_list.append((0, (50, 50), (199, 236)))
    return_list.append((0, (50, 50), (199, 210)))
    return_list.append((0, (50, 50), (199, 160)))
    return_list.append((0, (50, 50), (203, 142)))
    return_list.append((0, (50, 50), (203, 159)))
    return_list.append((0, (50, 50), (203, 211)))
    return_list.append((0, (50, 50), (203, 222)))
    return_list.append((0, (50, 50), (203, 209)))
    return_list.append((0, (50, 50), (203, 178)))
    return_list.append((0, (50, 50), (203, 150)))
    return_list.append((0, (50, 50), (203, 142)))
    return_list.append((0, (50, 50), (203, 131)))
    return_list.append((0, (50, 50), (213, 95)))
    return_list.append((0, (50, 50), (218, 35)))
    return_list.append((0, (50, 50), (223, 0)))
    return_list.append((0, (50, 50), (223, 0)))
    return_list.append((0, (50, 50), (230, 0)))
    return_list.append((0, (50, 50), (275, 71)))
    return_list.append((0, (50, 50), (275, 165)))
    return return_list


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

    return game_result, board, img_frames


def setup(client):  # Cog setup command
    client.add_cog(custom_images(client))
