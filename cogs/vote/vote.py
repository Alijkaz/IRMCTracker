from discord.ext.commands.errors import MissingRequiredArgument
from peewee import DoesNotExist

from modules.database import get_servers
from modules.database import DiscordVote as VoteDB
from modules.utils import get_beautified_dt

from discord import Embed
from discord.ext.commands import Cog, has_role, group

from dislash import SelectMenu, SelectOption

class Vote(Cog):
    """Voting system

    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.is_voting_enabled = False
    
    @group(invoke_without_command=True, aliases=['vt'])
    @has_role('root')
    async def voting(self, ctx):
        await ctx.send('No arguments detected')

    @voting.command()
    @has_role('root')
    async def clear(self, ctx):
        VoteDB.raw('DELETE FROM votes').execute()
        await ctx.send('Cleared vote table')

    @voting.command()
    @has_role('root')
    async def start(self, ctx, *, title_and_desc: str):
        # Title and description validating...
        params = title_and_desc.split("\n")

        # Alert user on missing arguments
        if (len(params) != 2): raise MissingRequiredArgument()
        
        title = params[0]
        description = params[1]

        servers = get_servers()

        options = []

        for server in servers:
            options.append(SelectOption(server.name, server.id))
        
        embed = Embed(title=f"💎 Vote | {title}", 
                        description=description + "\n\nسرور مورد نظر خودتون رو داخل باکس پایین انتخاب کنید", 
                        color=0xD7CCC8)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/533248248685789196/876398664254361620/vote.png')
        embed.set_footer(text=f"IRMCTracker - {get_beautified_dt()}", icon_url='https://cdn.discordapp.com/avatars/866290840426512415/06e4661be6886a7818e5ce1d09fa5709.webp?size=2048')

        msg = await ctx.send(
            embed=embed,
            components=[
                SelectMenu(
                    custom_id="best_server",
                    placeholder="سرور مورد نظر خودتون رو انتخاب کنید ❓",
                    max_values=1,
                    options=options
                )
            ]
        )

        self.bot.is_voting_enabled = True

        while self.bot.is_voting_enabled:
            inter = await msg.wait_for_dropdown()

            labels = [option.label for option in inter.select_menu.selected_options]
            values = [option.value for option in inter.select_menu.selected_options]
            
            await inter.reply(f"✅ {inter.author.mention} نظر شما ثبت شد! مرسی از اینکه وقت گذاشتی 😄", delete_after=3)
            
            VoteDB.insert(
                user_id = inter.author.id,
                server_id= values[0]
            ).on_conflict('replace').execute()


    @voting.command()
    @has_role('root')
    async def stop(self, ctx):
        if self.bot.is_voting_enabled:
            embed = Embed(title="⭕ Stopped Voting", description="I'm no longer listening to votes", color=0xD32F2F)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Voting is not started yet!')

    @voting.command(aliases=['results', 'r'])
    @has_role('root')
    async def result(self, ctx, *, title_and_desc):
        # Title and description validating...
        params = title_and_desc.split("\n")

        # Alert user on missing arguments
        if (len(params) != 2): raise MissingRequiredArgument()
        
        title = params[0]
        description = params[1]

        servers = get_servers()
        all_votes_count = 0

        #Looping through all server in database so that 
        # we can count and sort based on votes
        for server in servers:
            # Gonna check if server has any votes,
            # if it has, we count & store them
            try:
                # Try to count server votes
                server.votes_count = len(server.votes)
                # Add count to all count
                all_votes_count += server.votes_count
            # Excepts when server doesnt have any votes so we set them to 0 (we aint showing 0 vote servers)
            except DoesNotExist:
                server.votes_count = 0

        # Sorting servers based on votes_count (that we created in loop above)
        servers_sorted = sorted(servers, key=lambda x: x.votes_count, reverse=True)
        
        embed = Embed(title=f"💎 Top Servers | {title}",
                        description=description + f"\n\n💻 مجموع رای ها: {all_votes_count} رای", 
                        color=0x536DFE)
        i = 1
        prefix = '🏅'

        for server in servers_sorted:   
            # We will ignore 0 vote servers in result
            if (server.votes_count == 0):
                continue

            if i == 1:
                prefix = '🥇'
            elif i == 2:
                prefix = '🥈'
            elif i == 3:
                prefix = '🥉'

            embed.add_field(name=f"{prefix} {server.name}",
                                value=f"✌ {str(server.votes_count)} Votes",
                                inline=False)
            i += 1

        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/533248248685789196/876398664254361620/vote.png')
        embed.set_footer(text=f"IRMCTracker - {get_beautified_dt()}", icon_url='https://cdn.discordapp.com/avatars/866290840426512415/06e4661be6886a7818e5ce1d09fa5709.webp?size=2048')

        await ctx.send(embed=embed)

    @start.error
    @result.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Input arguments are wrong! Usage is: vote start [line #1 title] [line #2 description]")

def setup(client):
    client.add_cog(Vote(client))
