# Contribution Guide

## What I should prepare before starting contributing?

This project uses pipenv to work. Install pipenv through your package manager or by running `pip install pipenv`.
Then install everything by `pipenv install` command. Also, before testing anything, you must run `pipenv shell` if your
IDE didn't do that.

## How I should write my code?

PEP 8 is one requirement to code. If the code is new commands that output something to a user, you should do it as in
this template:

```python
@commands.Command()
async def template(ctx):
    lang = shared.load_server_language(ctx.message)
    _ = lang.gettext
    do_something()
    await ctx.send(_("message"))
```

This is used to ease work of translation, because programs never forgets to do something. Else you work without _() and
can remove anything related to it

Note that bot is intended to run from its root directory, and not src/.

after you done your work, run `python /usr/lib/python3.10/Tools/i18n/pygettext.py -d all -p src/locales src/` and then
simply do pull request with short description of changes, your code will be analyzed and commonly merged.

### I saw some unoptimised/potentially dangerous/bad code, how could I fix it?

Basically, fork the bot and do changes, then pull request to bot. Or if you don't want to do anything, create issue.
Your work will make this bot better anyway.

## I am native speaker of 'insert your language here' and I want to help with translation of the bot.

Sure! To help, fork bot, and do steps to make gettext language files. They include creating language folder, creating
LC_MESSAGES in it, adding `all.po` file by copying template.
Then translate by your favourite .po editor.