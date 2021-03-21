import discord
from discord.ext import commands
from datetime import datetime, timezone


class admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner = discord.ClientUser

    @commands.command(aliases=['BOTINFO', 'BotInfo', 'bot_info', 'info'])
    async def botinfo(self, ctx):

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

        fields = [("Name - prefix", f'{self.client.user.name} - \"{self.client.command_prefix}\"', False),
                  (":trophy: Owner", owner_id, True),
                  ('🦮Serving ', f'{mh} users / {len(list(self.client.guilds))} servers',
                   True), ("Favorite Cookbook", "Serving Humans", True),
                  ("⛭GitHub",
                   "[GitHub LINK](https://github.com/oklahomabot/picpal-discordbot)", True),
                  ("📝Invite me", "[Click Here to Add Me](https://discord.com/api/oauth2/authorize?client_id=822991442154750033&permissions=2684873792&scope=bot)", True)]


def setup(client):  # Cog setup command
    client.add_cog(admin(client))
