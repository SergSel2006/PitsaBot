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


def load_server_language(message):
    config = find_server_config(message)
    language = load_language(config["language"])
    return language


def load_language(lang):
    with open(
            pathlib.Path("data", "languages", f"{lang}.yml"), "r",
            encoding="utf8"
            ) as \
            lang:
        lang = yaml.load(lang, Loader=Loader)
        return lang


def find_server_config(message):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "r", encoding="utf8"
            ) as config:
        config = yaml.load(config, Loader=Loader)
        return config


def can_manage_channels():
    async def predicate(ctx):
        perms = ctx.author.top_role.permissions
        if perms.manage_channels or perms.administrator:
            return True
        else:
            await ctx.send(
                load_server_language(ctx.message)["misc"][
                    "not_enough_permissions"]
                )
            return False
    
    return commands.check(predicate)


class SettingsCog(commands.Cog):
    """Изменяет всяческие настроики сервера."""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.Command
    @can_manage_channels()
    async def prefix(self, ctx, prefix=None):
        """||descstart||
        ||shortstart||Меняет префикс.||shortend||
        ||longstart||Только для администраторов! Меняет префикс на
        указанный. Не советую ставить название команды как префикс.||longend||
        ||usage||префикс||end||
        ||descend||"""
        language = load_server_language(ctx.message)
        with open(
                pathlib.Path(
                    "data", "servers_config", str(ctx.guild.id),
                    "config.yml"
                    ),
                "r"
                ) as config:
            config = yaml.load(config, Loader)
            if prefix:
                config["prefix"] = prefix
                with open(
                        pathlib.Path(
                            "data", "servers_config", str(ctx.guild.id),
                            "config.yml"
                            ),
                        "w"
                        ) as config_raw:
                    yaml.dump(config, config_raw, Dumper)
                await ctx.send(
                    language["misc"][
                        "prefix_changed_successfully"]
                    )
            else:
                await ctx.send(
                    language["misc"]["current_prefix"] + config[
                        "prefix"]
                    )
    
    @commands.Command
    @can_manage_channels()
    async def modrole(self, ctx, mode):
        config = find_server_config(ctx.message)
        lang = load_server_language(ctx.message)
        roles = ctx.message.role_mentions
        if mode.lower() == "add":
            for role in roles:
                if role.id not in config["modroles"]:
                    config["modroles"].append(role.id)
                else:
                    await ctx.send(
                        lang["misc"]["role_in_list"].replace(
                            "$ROLE", role
                            )
                        )
            await ctx.send(lang["misc"]["roles_added"])
        elif mode.lower() == "remove":
            for role in roles:
                if role.id in config["modroles"]:
                    config["modroles"].remove(role.id)
                else:
                    await ctx.send
                    (
                        lang["misc"]["role_not_in_list"].replace(
                            "$ROLE", role
                            )
                    )
            await ctx.send(lang["misc"]["куьщмув"])
    
    @commands.Command
    @can_manage_channels()
    async def change_modlog_channel(self, ctx):
        """||descstart||
        ||shortstart||(де)Активирует modlog на указанном канале.||shortend||
        ||longstart||Только для администраторов! Включает модлог на
        указанный канал или выключает его посредством disable||longend||
        ||usage||канал/disable||end||
        ||descend||"""
        language = load_server_language(ctx.message)
        if "disable" not in ctx.message.content:
            with open(
                    pathlib.Path(
                        "data", "servers_config", str(ctx.guild.id),
                        "config.yml"
                        ),
                    "r"
                    ) as config:
                if "this" not in ctx.message.content:
                    channel = ctx.message.channel_mentions[0]
                else:
                    channel = ctx.channel
                config = yaml.load(config, Loader)
                if not config["modlog"]["enabled"]:
                    config["modlog"]["enabled"] = True
                config["modlog"]["channel"] = channel.id
                with open(
                        pathlib.Path(
                            "data", "servers_config",
                            str(ctx.guild.id),
                            "config.yml"
                            ),
                        "w"
                        ) as config_raw:
                    yaml.dump(config, config_raw, Dumper)
                    await ctx.send(
                        language["misc"]["modlog_activated"]
                        )
        
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
                            "data", "servers_config",
                            str(ctx.guild.id),
                            "config.yml"
                            ),
                        "w"
                        ) as config_raw:
                    yaml.dump(config, config_raw, Dumper)
                    await ctx.send(
                        language["misc"]["modlog_deactivated"]
                        )
    
    @commands.Command
    @can_manage_channels()
    async def chlang(self, ctx, language='en'):
        avaliable = ["ru", "en"]
        languagedict = load_server_language(ctx.message)
        configs = find_server_config(ctx.message)
        if language in avaliable:
            configs["language"] = language
            with open(
                    pathlib.Path(
                        "data", "servers_config", str(ctx.guild.id),
                        "config.yml"
                        ), "w", encoding="utf8"
                    ) as config:
                yaml.dump(configs, config, Dumper=Dumper)
            await ctx.send(
                languagedict["misc"]["language_changed_successfully"]
                )
        else:
            await ctx.send(languagedict["misc"]["invalid_language"])


def setup(bot):
    bot.add_cog(SettingsCog(bot, pathlib.Path(os.getcwd())))
