# ##################################################################################################
#  Copyright (c) 2022.                                                                             #
#        This program is free software: you can redistribute it and/or modify                      #
#        it under the terms of the GNU General Public License as published by                      #
#        the Free Software Foundation, either version 3 of the License, or                         #
#        (at your option) any later version.                                                       #
#                                                                                                  #
#        This program is distributed in the hope that it will be useful,                           #
#        but WITHOUT ANY WARRANTY; without even the implied warranty of                            #
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                             #
#        GNU General Public License for more details.                                              #
#                                                                                                  #
#        You should have received a copy of the GNU General Public License                         #
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.                    #
# ##################################################################################################

import atexit
import pathlib

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

from discord.ext import commands
import boto3

s3 = None


def upload_file(s3_client, file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = pathlib.Path(file_name).name

    # Upload the file
    response = s3_client.upload_file(file_name, bucket, object_name)


def download_file(s3_client, object_name, bucket, file_name=None):
    if file_name is None:
        file_name = object_name

    with open(file_name, "wb") as file:
        s3_client.download_fileobj(bucket, object_name, file)


def file_uploader(path):
    for file in pathlib.Path(path).iterdir():
        if file.is_dir():
            file_uploader(path / file.name)
        else:
            upload_file(s3, str(file), "data-serversconfig", str(file))


def list_s3_files():
    return [i["Key"] for i in s3.list_objects(
        Bucket="data-serversconfig")["Contents"]]


def file_downloader():
    for file_obj in list_s3_files():
        file = pathlib.Path(file_obj)
        if not file.parent.exists():
            file.parent.mkdir()
        else:
            if not file.exists():
                file.touch()
            else:
                download_file(s3, file_obj, "data-serversconfig", file)


class DataSyncerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def owner_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def upload_all(self, ctx):
        if await self.owner_check(ctx):
            file_uploader(pathlib.Path("data", "servers_config"))

    @commands.command(hidden=True)
    async def download_all(self, ctx):
        if await self.owner_check(ctx):
            file_downloader()


def setup(bot):
    global s3
    bot.add_cog(DataSyncerCog(bot))
    atexit.register(file_uploader, pathlib.Path("data", "servers_config"))
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        aws_access_key_id=bot.settings["Aws_tokens"][0],
        aws_secret_access_key=bot.settings["Aws_tokens"][1]
    )  # giving access to server configurations is unsafe, live with it :-)
    file_downloader()


def teardown(bot):
    atexit.unregister(file_uploader)
    file_uploader(pathlib.Path("data", "servers_config"))
