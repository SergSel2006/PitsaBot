#  Copyright (C) 2021  SergSel2006
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
    ) as lang:
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


def dump_server_config(message, config):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
            ), "w", encoding="utf8"
    ) as config_file:
        yaml.dump(config, config_file, Dumper=Dumper)


def can_manage_channels():
    async def predicate(ctx):
        perms = ctx.author.top_role.permissions
        if perms.manage_channels or perms.administrator or ctx.author.id == \
                ctx.guild.owner_id:
            return True
        else:
            return False

    return commands.check(predicate)


class SettingsCog(commands.Cog):

    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.Command
    @can_manage_channels()
    async def config(self, ctx, mode, *options):
        language = load_server_language(ctx.message)
        config = find_server_config(ctx.message)
        if mode.lower() == "prefix":
            config['prefix'] = options[0]
            dump_server_config(ctx.message, config)
            await ctx.send(
                language["misc"][
                    "prefix_changed_successfully"]
            )
        elif mode.lower() == "modrole":
            roles = ctx.message.role_mentions
            if options:
                if options[0].lower() == "add":
                    for role in roles:
                        if role.id not in config["modroles"]:
                            config["modroles"].append(role.id)
                        else:
                            await ctx.send(
                                language["misc"]["role_in_list"].replace(
                                    "$ROLE", role.mention
                                )
                            )
                    dump_server_config(ctx.message, config)
                    await ctx.send(language["misc"]["roles_added"])
                elif options[0].lower() == "remove":
                    for role in roles:
                        if role.id in config["modroles"]:
                            config["modroles"].remove(role.id)
                        else:
                            await ctx.send
                            (
                                language["misc"]["role_not_in_list"].replace(
                                    "$ROLE", role.mention
                                )
                            )
                    dump_server_config(ctx.message, config)
                    await ctx.send(language["misc"]["roles_removed"])
            else:
                await ctx.send(" ".join([ctx.guild.get_role(i).mention for i
                                         in config["modroles"]]))
        elif mode.lower() == "modlog":
            if options[0].lower() == "enable":
                if config["modlog"]["channel"]:
                    config["modlog"]["enabled"] = True
                    dump_server_config(ctx.message, config)
                    await  ctx.send(language["misc"]["modlog_activated"])
                else:
                    await ctx.send(language["misc"]["need_modlog_channel"])
            elif options[0].lower() == "channel":
                if options[1].lower() != "this":
                    channel = ctx.message.channel_mentions[0]
                else:
                    channel = ctx.channel
                config["modlog"]["channel"] = channel.id
                dump_server_config(ctx.message, config)
                await ctx.send(language["misc"]["modlog_channel_set"])
            elif options[0].lower() == "disable":
                config["modlog"]["enabled"] = False
                dump_server_config(ctx.message, config)
                await ctx.send(language["misc"]["modlog_deactivated"])
        elif mode.lower() == "language":
            available = []
            for i in pathlib.Path("data", "languages").iterdir():
                available.append(i.stem)
            if options[0] in available:
                config["language"] = options[0]
                dump_server_config(ctx.message, config)
                await ctx.send(
                    language["misc"]["language_changed_successfully"]
                )
            else:
                await ctx.send(language["misc"]["invalid_language"])
        elif mode.lower() == "trigger":
            if options[0] == "enable":
                config["everyonetrigger"] = True
                dump_server_config(ctx.message, config)
            else:
                config["everyonetrigger"] = False
                dump_server_config(ctx.message, config)


def setup(bot):
    bot.add_cog(SettingsCog(bot, pathlib.Path(os.getcwd())))
