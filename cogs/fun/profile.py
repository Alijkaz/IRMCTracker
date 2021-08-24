from discord import Embed

from discord.ext.commands import Cog, command

from modules.database import Player as PlayerDB
from peewee import DoesNotExist
from modules.api.hypixel import HypixelPlayer
from modules.api import Player
from modules.utils import *

from random import randint

import json

class Profile(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=['prof','p','player'])
    async def profile(self, ctx, username:str = None):
        # Check if username is specified in the command
        if not username:
            embed = Embed(title=f"{self.bot.emoji('steve_think')} Khob alan donbal ki hasti dabsh?", 
                            description="Usage: .profile [username] | .profile Alijk", 
                            color=0xFF0000)
            return await ctx.send(embed=embed)
        
        player = Player(username)

        # Check if username is valid and exists
        if not player.is_valid():
            embed = Embed(title=f"{self.bot.emoji('steve_think')} Ki hast? {username} ro nemishnasam!", 
                            color=0xFF0000)
            return await ctx.send(embed=embed)

        try:
            player_db = PlayerDB.get(PlayerDB.username == username)

            hypixel_player = json.loads(player_db.hypixel_data)
            hypixel_status = hypixel_player['status']

        except DoesNotExist:
            hypixel = HypixelPlayer(username)
            hypixel_player = hypixel.get_player()
            hypixel_status = hypixel_player['status']

            player_db = PlayerDB(
                username=username,
                uuid=player.get_uuid(),
                hypixel_data=json.dumps(hypixel_player),
                minecraft_data=json.dumps(player.get_player_data()),
            )
            player_db.save()

        embed = Embed(
            title=f"{self.bot.emoji('steve_dab')} ⌠・Profile {username.capitalize()}・⌡", 
            color=randint(0, 0xffffff)
        )

        embed.add_field(
            name=f"{self.bot.emoji('history')} Username Haye Ghabli",
            value=' | '.join(player.get_other_usernames()),
            inline=True
        )

        embed.add_field(
            name="📅 Zaman Sakhte Shodan",
            value=player.get_created_ago(),
            inline=True
        )

        embed.set_thumbnail(
            url=player.get_head_image()
        )

        embed.set_footer(
            text=f"IRMCTracker ・ {get_beautified_dt()}", 
            icon_url='https://cdn.discordapp.com/avatars/866290840426512415/06e4661be6886a7818e5ce1d09fa5709.webp?size=2048'
        )

        embed.add_field(
            name=f"{self.bot.emoji('question_new')} Hypixel",
            value="Play Dade" if hypixel_player else "Play Nadade",
            inline=False
        )

        if hypixel_player:
            embed.add_field(
                name=f"{self.bot.emoji('first')} Avalin vorud be hypixel",
                value=timestamp_ago(hypixel_player['player']['firstLogin'] / 1000),
                inline=True
            )
            
            embed.add_field(
                name="⭕ Akharin vorud be hypixel",
                value=timestamp_ago(hypixel_player['player']['lastLogin'] / 1000),
                inline=True
            )

            try:
                last_game = hypixel_player['player']['mostRecentGameType']
            except KeyError:
                last_game = 'Not Shown'

            embed.add_field(
                name=f"{self.bot.emoji('play')} Akharin Gamemode",
                value=str(last_game).lower().capitalize(),
                inline=False
            )

            try:
                bedwars_level = hypixel_player['player']['achievements']['bedwars_level']
            except KeyError:
                bedwars_level = 0

            embed.add_field(
                name=f"{self.bot.emoji('up_new')} Bedwars Level",
                value=bedwars_level,
                inline=True
            )

            try:
                bedwars_win = hypixel_player['player']['achievements']['bedwars_wins']
            except KeyError:
                bedwars_win = 0

            embed.add_field(
                name="🔪 Bedwars Wins",
                value=bedwars_win,
                inline=True
            )

            try:
                mc_version = hypixel_player['player']['mcVersionRp']
            except KeyError:
                mc_version = 'Not Shown'

            embed.add_field(
                name=f"{self.bot.emoji('alert')} Version",
                value=mc_version,
                inline=False
            )

            try:
                is_online = hypixel_status['online']
            except KeyError:
                is_online = False

            embed.add_field(
                name=f"{self.bot.emoji('steve_think')} Alan dar Hypixel",
                value=f"Online" if is_online else f"Offline",
                inline=True
            )
            
            if is_online:
                embed.add_field(
                    name=f"{self.bot.emoji('controller')} Dar hale bazi kardan",
                    value=str(hypixel_status['mode']).capitalize(),
                    inline=True
                )

        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Profile(bot))