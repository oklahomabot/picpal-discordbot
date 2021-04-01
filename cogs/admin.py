import discord
from discord.ext import commands
from datetime import datetime, timezone


class admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.command(aliases=['BOTINFO', 'BotInfo', 'bot_info', 'info'])
    async def botinfo(self, ctx):
        '''General Information about PicPal'''
        embed = discord.Embed(
            title='🤖Bot Information🤖', colour=discord.Colour.blue(), timestamp=datetime.now(tz=timezone.utc))

        embed.set_thumbnail(url=self.client.user.avatar_url)

        mh = 0
        for i in self.client.guilds:

            mh += len([m for m in i.members if not m.bot])

        try:
            owner_id = f'<@!{self.client.owner_id}>'
        except:
            owner_id = 'Not defined in commands.Bot.owner_id'

        fields = [("Name - prefix", f'{self.client.user.name} - \"{self.client.command_prefix}\"', True),
                  (":trophy: Owner", owner_id, True),
                  ('🦮Serving ', f'{mh} users / {len(list(self.client.guilds))} servers',
                   True), ("Favorite Movie", "Terminator", True),
                  ("⛭GitHub",
                   "[GitHub LINK](https://github.com/oklahomabot/picpal-discordbot)", True),
                  ("📝Invite me", "[Click Here to Add Me](https://discord.com/api/oauth2/authorize?client_id=822991442154750033&permissions=2684873792&scope=bot)", True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(
            text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['erase'], hidden=True)
    async def purge(self, ctx, num=2):
        'Admin delete'
        if ctx.author.id == self.client.owner_id:
            await ctx.channel.purge(limit=num+1)
        else:
            if ctx.author.id == 793433316258480128:
                await ctx.send('Not for you **sniper** :smile:')
            else:
                await ctx.send("I don\'t feel compliant right now")

    @commands.command(aliases=['cmdcount', 'cmd_count'], hidden=False)
    async def commands(self, ctx):

        commands_desc = ''
        '''
        for command in self.client.commands:
            commands_desc += f'{command.name} - {command.help}\n'
        '''
        await ctx.send(f'I have {len(self.client.commands)} total commands.')


def setup(client):  # Cog setup command
    client.add_cog(admin(client))
