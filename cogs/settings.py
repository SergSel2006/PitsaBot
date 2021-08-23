import os
import pathlib

import yaml
from discord.ext import commands

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper


def can_manage_channels():
    async def predicate(ctx):
        perms = ctx.author.top_role.permissions
        return perms.manage_channels or perms.administrator
    
    return commands.check(predicate)


class SettingsCog(commands.Cog, name="настроики сервера"):
    """Изменяет всяческие настроики сервера."""
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.Command
    @can_manage_channels()
    async def prefix(self, ctx, prefix):
        """||descstart||
        ||shortstart||Меняет префикс.||shortend||
        ||longstart||Только для администраторов! Меняет префикс на
        указанный. Не советую ставить название команды как префикс.||longend||
        ||usage||префикс||end||
        ||descend||"""
        with open(
                pathlib.Path(
                        "data", "servers_config", str(ctx.guild.id),
                        "config.yml"
                        ),
                "r"
                ) as config:
            if prefix:
                config = yaml.load(config, Loader)
                config["prefix"] = prefix
                with open(
                        pathlib.Path(
                                "data", "servers_config", str(ctx.guild.id),
                                "config.yml"
                                ),
                        "w"
                        ) as config_raw:
                    yaml.dump(config, config_raw, Dumper)
                await ctx.send("Префикс успешно сменён!")
            else:
                await ctx.send("Укажите префикс!")
    
    @commands.Command
    @can_manage_channels()
    async def change_modlog_channel(self, ctx):
        """||descstart||
        ||shortstart||(де)Активирует modlog на указанном канале.||shortend||
        ||longstart||Только для администраторов! Включает модлог на
        указанный канал или выключает его посредством disable||longend||
        ||usage||канал/disable||end||
        ||descend||"""
        if not "disable" in ctx.message.content:
            with open(
                    pathlib.Path(
                            "data", "servers_config", str(ctx.guild.id),
                            "config.yml"
                            ),
                    "r"
                    ) as config:
                if not "this" in ctx.message.content:
                    channel = ctx.message.channel_mentions[0]
                else:
                    channel = ctx.channel
                config = yaml.load(config, Loader)
                if not config["modlog"]["enabled"]:
                    config["modlog"]["enabled"] = True
                config["modlog"]["channel"] = channel.id
                with open(
                        pathlib.Path(
                            "data", "servers_config", str(ctx.guild.id),
                            "config.yml"
                            ),
                        "w"
                        ) as config_raw:
                    yaml.dump(config, config_raw, Dumper)
                    await ctx.send("Модлог активирован")

        else:
            with open(
                    pathlib.Path(
                        "data", "servers_config", str(ctx.guild.id),
                        "config.yml"
                        ),
                    "r"
                    ) as config:
                config = yaml.load(config, Loader)
                if config["modlog"]["enabled"]:
                    config["modlog"]["enabled"] = False
                with open(
                        pathlib.Path(
                            "data", "servers_config", str(ctx.guild.id),
                            "config.yml"
                            ),
                        "w"
                        ) as config_raw:
                    yaml.dump(config, config_raw, Dumper)
                    await ctx.send("Модлог деактивирован")


def setup(bot):
    bot.add_cog(SettingsCog(bot, pathlib.Path(os.getcwd())))
