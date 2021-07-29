import os
import pathlib

from discord.ext import commands
import yaml


class SettingsCog(commands.Cog, name=""):
    """"""

    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.Command
    async def prefix(self, ctx, prefix):
        """Меняет префикс"""
        with open(pathlib.Path(f"data\\servers_config\\{ctx.guild.id}.yml"),
                  "r") as config:
            if prefix:
                config = yaml.load(config, yaml.CLoader)
                config["prefix"] = prefix
                with open(pathlib.Path(
                        f"data\\servers_config\\{ctx.guild.id}.yml"),
                          "w") as config_raw:
                    yaml.dump(config, config_raw, yaml.CDumper)
                await ctx.send("Префикс успешно сменён!")
            else:
                await ctx.send("Укажите префикс!")

    @commands.Command
    async def change_modlog_channel(self, ctx):
        with open(pathlib.Path(f"data\\servers_config\\{ctx.guild.id}.yml"),
                  "r") as config:
            channel = ctx.message.channel_mentions[0]
            config = yaml.load(config, yaml.CLoader)
            if not config["modlog"]["enabled"]:
                config["modlog"]["enabled"] = True
            config["modlog"]["channel"] = channel.id


def setup(bot):
    bot.add_cog(SettingsCog(bot, pathlib.Path(os.getcwd())))
