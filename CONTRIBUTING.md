# Contribution Guide

## What I should prepare before starting contributing?

Before you start writing code, do your usual steps to create new project(create one in your IDE, create virtual
enviroment, etc.) and then you should install all packages by `pip install -r requirements.txt`
and then you can write your code, very easy. Don't foreget to use development branch!

## How I should write my code?

PEP 8 is one requirement to code. If the code is new commands that output something to a user, you should do it as in
this template:

```python
@commands.Command()
async def template(ctx):
    lang = load_server_language(ctx.message)
    await ctx.send(lang['misc']['some-translation'])
```

And also add something like `some-translation: something` in data/languages/one_of_the_languages.yml file under misc.
Help of the commands should be like this:

```yaml
help:
  some_command:
    short: something
    long: this command does something
    optional: optional argument
    returns: message
    usage: required argument
```

after you done your work, simply do pull requiest with short description of changes, your code will be analyzed and
commonly merged.

### I saw some unoptimised/potentially dangerous/bad code, how could I fix it?

Basically, fork the bot and do changes, then pull requiest to bot. Or if you don't want to do anything, create issue.
Your work will make this bot better.

## I am native speaker of 'insert your language here' and I want to help with translation of the bot.

Sure! To help, fork bot, add your language in the data/languages folder (name of file like de.yml), and then you can use
small python script named rebase_languages.py to create everything, and then translate! After work done don't forget
about pull requiest.
