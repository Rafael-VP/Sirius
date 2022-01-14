from discord.ext import commands
from discord_slash import SlashCommand
import os
import sys
import json
import time


with open("data/config.json", "r") as f:
    config = json.load(f)

client = commands.Bot(command_prefix=".")
slash = SlashCommand(client, sync_commands=True)


def owner_check(ctx):
    """Check if command author is the bot owner through ID."""
    return ctx.author.id == config["owner_id"]


# DEVELOPER COMMANDS


@slash.slash(name="restart", guild_ids=[config['guild_id']])
@commands.check(owner_check)
async def restart(ctx):
    """Restarts the application, resetting all variables and running
    commands/functions."""
    await ctx.send("Restarting application...")
    os.execv(sys.executable, ['python'] + sys.argv)


@slash.slash(name="load", guild_ids=[config['guild_id']])
@commands.check(owner_check)
async def load(ctx, cog):
    """Loads cogs on the main application."""
    client.load_extension(f'cogs.{cog}')
    await ctx.send(f"The cog {cog} was loaded.")


@slash.slash(name="unload", guild_ids=[config['guild_id']])
@commands.check(owner_check)
async def unload(ctx, cog):
    """Unloads cogs on the main application."""
    client.unload_extension(f'cogs.{cog}')
    await ctx.send(f"The cog {cog} was unloaded.")


@slash.slash(name="reload", guild_ids=[config['guild_id']])
@commands.check(owner_check)
async def reload(ctx, cog):
    """Reloads cogs on the main application."""
    client.unload_extension(f'cogs.{cog}')
    client.load_extension(f'cogs.{cog}')
    await ctx.send(f"The cog {cog} was reloaded.")


# GENERAL COMMANDS

@slash.slash(name="github")
async def github(ctx):
    """Displays a link to the project's GitHub repository."""
    await ctx.send("https://github.com/Rafael-VP/Sirius")


@slash.slash(name="ping")
async def ping(ctx):
    """Displays the bot's current websocket and API latency."""
    start_time = time.time()
    message = await ctx.send("Testing Ping...")
    end_time = time.time()

    await message.edit(content=(f":ping_pong: Pong!\nBot: "
                                f"{round(client.latency * 1000)}ms\nAPI: "
                                f"{round((end_time - start_time) * 1000)}ms"))

# Automatically loads cogs at application execution.
for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(config['token'])
