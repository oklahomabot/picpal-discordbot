import discord
import requests
import os
import urllib.parse
from discord.ext import commands


class testing(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.Cog.listener("on_message")
    async def reaction_stuff(self, message):
        '''
        Listens for messages that start with any tick marks (accent grave)
        Reacts to message and awaits message author to react with same
        Non reaction is timed out and reaction emoji removed from message
        '''
        if (message.author == self.client.user):  # Not the BOT
            return
        # Server Specific
        if message.guild.id not in [790518150306332673, 811481989407965226, 795911343445508107]:
            return

        if not chr(96) in message.content:
            return

        my_emoji = u"\U0001F916"  # Robot emoji unicode (U+1F916)
        await message.add_reaction(my_emoji)

        def check(reaction, user):
            return (user == message.author) and (str(reaction.emoji) == my_emoji) and (reaction.message == message)

        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
        except:
            await message.remove_reaction(my_emoji, self.client.user)
            return  # Exit Function (Timed Out)

        # Author pressed correct emoji in time
        await message.clear_reaction(my_emoji)
        desc = (('[Image Produced By Carbon.now API](https://carbon.now.sh/)'))
        embed = discord.Embed(title=('PLAYING WITH CODE'),
                              description=desc, colour=discord.Colour.light_gray())
        embed.set_thumbnail(url=message.author.avatar_url_as(size=32))

        getVars = {'code': code_for_url(message.content),
                   'fontSize': '18px',
                   'backgroundColor': 'rgba(1, 252, 207, 100)',
                   'paddingHorizontal': '23px', 'paddingVertical': '23px',
                   'theme': 'Panda'}
        url = 'https://carbonnowsh.herokuapp.com/?'
        complete_url = url+urllib.parse.urlencode(getVars)
        failure = False
        try:
            response = requests.get(complete_url)
        except:
            failure = True
        if failure or response.status_code != 200:
            await message.channel.send('Something wrong happened with your request')
            return

        outpath = os.path.join('./', 'cogs', 'temp.png')
        with open(outpath, 'wb') as output:
            output.write(response.content)
            output.close()

        await message.channel.send(embed=embed)
        await message.channel.send(file=discord.File(outpath))
        if os.path.exists(outpath):
            os.remove(outpath)
        return


def code_for_url(msg):
    code = msg[msg.find(chr(96)):]  # remove pre-code text
    code = code.lstrip(chr(96))     # remove tick marks from start
    break_position = code.find("\n")
    if break_position != -1:        # remove 'language' if any
        code = code[(break_position+1):]
    break_position = code.find(chr(96))
    if break_position != -1:        # remove after code text
        code = code[:(break_position):]
    code = urllib.parse.quote_plus(code)
    return code


def setup(client):  # Cog setup command
    client.add_cog(testing(client))
