import discord
from discord.ext import commands
from datetime import datetime, timezone


class admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.Cog.listener("on_command")
    async def msg_display(self, ctx):
        '''Console Command Log'''
        if (ctx.message.author == self.client) or (ctx.author.id == self.client.owner_id):
            return
        timestamp = datetime.now(tz=timezone.utc)
        print(
            f'{timestamp[:17]} User {ctx.message.author.display_name} in guild {ctx.guild.name} sent {ctx.message.content}')

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
        'Admin message delete'
        if ctx.author.id == self.client.owner_id:
            await ctx.channel.purge(limit=num+1)
        else:
            await ctx.send(f"I don\'t feel compliant right now {ctx.author.display_name}")

    @commands.command(aliases=['cmdcount', 'cmd_count'], hidden=False)
    async def command_count(self, ctx):
        '''Returns current number of bot commands'''
        alias_count = 0
        for command in self.client.commands:
            alias_count += len((command.aliases))+1
        await ctx.send((f'I process {len(self.client.commands)+alias_count} commands total.\n') +
                       (f'{len(self.client.commands)} command functions + {alias_count} aliases'))


def setup(client):  # Cog setup command
    client.add_cog(admin(client))
