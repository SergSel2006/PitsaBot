#  Copyright (c) 2022.
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This script rebases all language files to have keys on the same position
also if there is keys in a bot's main language, but in another language
they're missing, it add '<MISSING TRANSLATION>' to this key"""

import pathlib

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

for language in [x for x in pathlib.Path().iterdir() if x.suffix == ".yml"]:
    with open(language, "r", encoding="utf-8") as language_source:
        lang = yaml.load(language_source, Loader)

    with open(language, "w", encoding="utf-8") as language_source:
        yaml.dump(lang, language_source, Dumper, allow_unicode=True)

main_lang = pathlib.Path("ru.yml")


def diff(dict1: dict, dict2: dict):
    same = True
    if dict2 is None:
        dict2 = dict1.copy()
        for i in tuple(dict2.keys()):
            if type(dict2[i]) != dict:
                dict2[i] = "<MISSING TRANSLATION>"
            else:
                dict2[i] = None
                dict2[i], _ = diff(dict1[i], dict2[i])
        return dict2, False
    for i in tuple(dict1.keys()):
        if i not in tuple(dict2.keys()):
            dict2[i] = "<MISSING TRANSLATION>"
            same = False
        if type(dict2[i]) == dict:
            dict2[i], _ = diff(dict1[i], dict2[i])
            if not _:
                same = _
    return dict2, same


with open(main_lang, "r", encoding="utf-8") as main:
    main_dict = yaml.load(main, Loader)
    for i in [x for x in pathlib.Path().iterdir() if x.suffix == ".yml" and
                                                     x.stem != "ru"]:
        with open(i, "r+", encoding="utf-8") as nonmain:
            nonmain_dict = yaml.load(nonmain, Loader)
            nonmain_dict, same = diff(main_dict, nonmain_dict)
            if not same:
                print("Something's wrong with " + i.stem + " language!")
                nonmain.seek(0)
                yaml.dump(nonmain_dict, nonmain, Dumper)
