import discord as d
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from pymongo import MongoClient
import rolldice
import re
import json


with open("data/config.json") as f:
    setup = json.load(f)

# Connect to the database and load the character collection.
client = MongoClient(setup['connection_string'])
db = client.SiriusDB
collection = db.combat_trackers


class CombatTracker(commands.Cog):
    """Handles all combat tracker interactions."""
    def __init__(self, client):
        self.client = client

    def make_tracker(self, results):
        """Assembles a combat tracker."""
        turns = "```yaml\n"
        longest = 0
        counter = 1

        for i in results['turns']:
            if len(i) > longest:
                longest = len(i)

        for i in results['entities']:
            if counter == results['turn']:
                turns += f"\n>>{i}:".ljust(longest + 6) + \
                    str(results['entities'][i]).rjust(2)
                counter += 1
            else:
                turns += f"\n{i}:".ljust(longest + 6) + \
                    str(results['entities'][i]).rjust(2)
                counter += 1

        turns = turns + "\u200b```"
        embed = d.Embed(title="Combat Tracker",
                        description=f"Turn {results['turn']} - Round "
                                    f"{results['round']}\n{turns}")

        return embed

    @commands.Cog.listener()
    async def on_guild_channel_delete(ctx, channel):
        query = {"_id": channel.id}
        results = collection.find_one(query)

        if results:
            collection.delete_one(query)

    @cog_ext.cog_slash(name="combattracker",
                       description="Track, display and control order of "
                                   "combat.",
                       options=[
                        create_option(
                            name="command",
                            description="Command to be executed.",
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="next", value="next"),
                                create_choice(name="previous",
                                              value="previous"),
                                create_choice(name="sort", value="sort"),
                                create_choice(name="add", value="add"),
                                create_choice(name="remove", value="remove"),
                                create_choice(name="reset", value="reset")
                            ]),
                        create_option(
                            name="name",
                            description="Entity to be added to the turn "
                                        "order.",
                            option_type=3,
                            required=False
                            ),
                        create_option(
                            name="initiative",
                            description="Added entity's position on the turn"
                                        "order. Can either be a number or a "
                                        "dice expression.",
                            option_type=3,
                            required=False
                        )])
    async def combattracker(self, ctx, command="", name="", initiative=0):
        """Handles combat tracker interactions."""
        channel = ctx.channel.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if not results:
            msg = await ctx.send("Creating new combat tracker...")
            collection.insert_one({"_id": channel, "entities": {}, "turn": 1,
                                   "round": 1, "turns": []})
            await msg.edit(content="Combat tracker created successfully.")
            results = collection.find_one(query)

        if not command:
            embed = self.make_tracker(results)

            await ctx.send(embed=embed)

        elif command == "add":
            # Adds an entity to the combat tracker.
            if len(name) > 15:
                await ctx.send("Entity names may only be up to 15 characters"
                               "long.")
                return

            elif name in results['turns']:
                await ctx.send("Entity name unavailable.")
                return

            elif not re.match(string=name, pattern="^[a-zA-Z0-9_.-]*$"):
                await ctx.send("Entity name contains forbidden characters.")
                return

            elif len(results['turns']) > 25:
                await ctx.send("Combat trackers may only have up to 25 "
                               "entities at a time.")
                return

            try:
                # Test if initiative is an int or a roundable float.
                initiative = round(initiative)

            except Exception:
                try:
                    r, e = rolldice.roll_dice(initiative)
                    initiative = r

                except Exception:
                    await ctx.send(f"''{initiative}'' is not a valid "
                                   "initiative.")
                    return

            results['turns'].append(name)
            results['entities'][name] = initiative

            collection.update_one({"_id": channel}, {"$set": {"entities":
                                  results['entities'], "turns":
                                  results['turns']}})

            await ctx.send("Entity added to the turn order succesfully.")

        elif command == "remove":
            # Removes an entity from the combat tracker
            if name not in results['turns']:
                await ctx.send(f"Entity ''{name}'' not found.")
                return

            results['turns'].remove(name)
            del results['entities'][name]

            collection.update_one({"_id": channel}, {"$set": {"entities":
                                  results['entities'], "turns":
                                  results['turns']}})

            await ctx.send("Entity removed from turn order successfully.")

        elif command == "reset":
            # Removes all entities from the combat tracker and sets the current
            # round and turn to 1.
            await ctx.send("The currently active combat tracker will be reset."
                           " This process is irreversible. Do you wish to "
                           "proceed? (y/n)")

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel\
                    and msg.content.lower() in ['y', 'n']

            msg = await self.client.wait_for("message", check=check,
                                             timeout=30)

            if msg.content.lower() == "y":

                results['turns'] = []
                results['entities'] = {}
                results['turn'] = 1
                results['round'] = 1

                collection.update_one({"_id": channel}, {"$set":
                                      {"entities": results['entities'],
                                       "turns": results['turns'],
                                       "turn": results['turn'],
                                       "round": results['round']}})

                await ctx.send("Combat tracker reset successfully.")
                return

            else:
                await ctx.send("Combat tracker reset order cancelled.")
                return

        elif command == "sort":
            # Sorts all entities on the combat tracker through initiative.
            results['entities'] = {k: v for k, v in
                                   sorted(results['entities'].items(),
                                          key=lambda item: item[1],
                                          reverse=True)}

            collection.update_one({"_id": channel}, {"$set":
                                  {"entities": results['entities']}})

            await ctx.send("Turn order sorted successfully.")
            return

        elif command == "next":
            # Advances to the next turn of combat, changing the currently
            # active entity and the turn number. If the turn number exceeds
            # the number of entities on the tracker, a round is passed.
            if len(results['turns']) == 0:
                await ctx.send("Turn order is empty.")
                return

            if len(results['turns']) == results['turn']:
                results['turn'] = 1
                results['round'] += 1
            else:
                results['turn'] += 1

            collection.update_one({"_id": channel}, {"$set":
                                  {"turn": results['turn'],
                                   "round": results['round']}})

            embed = self.make_tracker(results)

            await ctx.send(embed=embed)
            return

        elif command == "previous":
            # Reverts to the previous round of combat, changing the currently
            # active entity and the turn number. If the turn number becomes 0,
            # the round is reverted, and the turn number becomes the total
            # amount of entities in the tracker. If round is already 1, an
            # error gets returned.
            if len(results['turns']) == 0:
                await ctx.send("Turn order is empty.")
                return

            if results['turn'] == 1:
                if results['round'] == 1:
                    await ctx.send("Combat tracker cannot be reverted.")
                    return

                results['turn'] = len(results['turns'])
                results['round'] -= 1
            else:
                results['turn'] -= 1

            collection.update_one({"_id": channel}, {"$set":
                                  {"turn": results['turn'],
                                   "round": results['round']}})

            embed = self.make_tracker(results)

            await ctx.send(embed=embed)
            return


def setup(client):
    client.add_cog(CombatTracker(client))
