import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
import rolldice
import modules.utility as u
from pymongo import MongoClient
import json


with open("data/config.json") as f:
    setup = json.load(f)

# Connect to the database and load the character collection.
client = MongoClient(setup['connection_string'])
db = client.SiriusDB
collection = db.dicebags


class Dicebag(commands.Cog):
    """Handles dicebag interactions."""

    def __init__(self, client):
        self.client = client

    def has_numbers(self, inputString):
        """Check if a string contains any numbers."""
        return any(char.isdigit() for char in inputString)

    def repeat_roll(self, amount, die):
        #  need to put this in a module somewhere
        """Repeats any given roll {amount} times and returns the result with
        each roll separated by a newline character."""
        re = ""
        ex = ""

        for i in range(0, amount):
            result, explanation = rolldice.roll_dice(die)
            re += f", {str(result)}"
            ex += f", {str(explanation)}"

        return re[2:], ex[2:]

    def check_roll(self, string):
        """Checks if a string is a valid roll or mathematical operation."""
        flag_1 = False
        flag_2 = False
        flag_3 = False

        for i in string:
            if i.isalpha():
                flag_1 = True

            if i.isdigit():
                flag_2 = True

            if i in ['+', '-', '*', '/', '%', '.']:
                flag_3 = True

        return flag_1 and flag_2 or flag_3

    @cog_ext.cog_slash(name="dicebag",
                       description="An inventory for storing and rolling "
                                   "dice.",
                       options=[
                        create_option(
                            name="command",
                            description="Command to be executed. Ommit to "
                                        "display the dicebag's contents.",
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="add", value="add"),
                                create_choice(name="remove", value="remove"),
                                create_choice(name="purge", value="purge"),
                                create_choice(name="roll", value="roll")
                            ]),
                        create_option(
                            name="name",
                            description="Name used to call a dice roll "
                                        "from the bag.",
                            option_type=3,
                            required=False
                        ),
                        create_option(
                            name="value",
                            description="Dice roll to be added to the "
                                        "bag. Ex.: 1d20 + 5.",
                            option_type=3,
                            required=False
                        )])
    async def dicebag(self, ctx, command="", name="", *, value=""):
        """"Displays and handles dicebag commands. A dicebag is a dedicated
        user inventory for saving and rolling dice expressions. A user may have
        a single dicebag containing up to 20 items at a time."""
        author = ctx.author.id
        value = u.list_to_str(value)
        query = {"_id": author}
        dicebags = collection.find_one(query)

        if not dicebags:
            msg = await ctx.send("Creating dicebag...")
            collection.insert_one({"_id": author})
            await msg.edit(content="Dicebag created successfully.")
            return

        if not command:
            dicebag = ""
            cursor = 0
            longest = ""

            for i in dicebags:
                if len(i) > len(longest):
                    longest = i

            for i in dicebags:
                if i != "_id":
                    dicebag += f"\n{i}:".ljust(len(longest) + 3) + \
                        f"{dicebags[i]}"
                    cursor += 1

            if len(dicebag) == 0:
                desc = "```yaml\nYour dicebag is empty.```"
            else:
                desc = f"```yaml\n{dicebag}\u200b```"

            embed = discord.Embed(title=f"{str(ctx.author)[:-5]}'s Dicebag",
                                  description=desc)

            await ctx.send(embed=embed)
            return

        elif command == 'add':
            if "d1!" in value:
                await ctx.send("Invalid dice roll.")
                return

            if '#' in value and self.has_numbers(value):
                partitioned_dice = value.partition('#')
                die = partitioned_dice[2]
                amount = int(partitioned_dice[0])

                if amount > 100:
                    await ctx.send("Oversized dice roll.")
                    return

                try:
                    r, e = rolldice.roll_dice(die)
                except Exception:
                    await ctx.send("Invalid dice roll.")
                    return

            else:
                if (not self.check_roll(value) or "d1!" in value or
                        len(value.replace(' ', '')) > 10):
                    # Exploding dice can get stuck on a loop otherwise
                    await ctx.send("Invalid dice roll.")
                    return

                try:
                    r, e = rolldice.roll_dice(value)
                except Exception:
                    await ctx.send("Invalid dice roll.")
                    return

            value = "".join(value)
            counter = 0
            rolls = []

            if len(value.replace(' ', '')) > 10:
                await ctx.send("Oversized dice roll.")
                return

            if dicebags is not None:
                for i in dicebags:
                    counter += 1
                    rolls.append(i)

            counter -= 1

            if counter == 20:
                await ctx.send("You may only have up to 20 rolls in your "
                               "dicebag at a time.")
                return

            elif name in rolls or name == "_id":
                await ctx.send("Name is unavailable.")
                return

            elif len(name) > 15:
                await ctx.send("Name exceeds maximum character length.")
                return

            collection.update_one({"_id": author}, {"$set": {name: value}})

            await ctx.send("Dicebag updated successfully.")
            return

        elif command == 'remove':
            rolls = []

            if not dicebags:
                await ctx.send("Item not found.")
                return

            for i in dicebags:
                if i != "_id":
                    rolls.append(i)

            if i not in rolls:
                await ctx.send("Item not found.")
                return

            collection.update_one({"_id": author}, {"$unset":
                                  {name: 1}})

            await ctx.send("Dicebag updated successfully.")
            return

        elif command == 'purge':
            if not dicebags:
                await ctx.send("Your dicebag is already empty.")
                return

            await ctx.send("Dicebag will be purged. This process is "
                           "irreversible. Do you confirm? (y/n)")

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel\
                        and msg.content.lower() in ['y', 'n']

            try:
                msg = await self.client.wait_for("message", check=check,
                                                 timeout=30)

                if msg.content.lower() == 'y':
                    for i in dicebags:
                        if i != "_id":
                            collection.update_one({"_id": author}, {"$unset":
                                                  {i: 1}})

                    await ctx.send("Dicebag updated successfully.")

                elif msg.content.lower() == 'n':
                    await ctx.send("Dicebag purge request cancelled.")
                    return

            except Exception:
                await ctx.send("Request timed out after 30 seconds.")
                return

        elif command == 'roll':
            try:
                roll = dicebags[name]
            except Exception:
                await ctx.send("Item not found.")
                return

            if '#' in roll:
                partitioned_dice = roll.partition('#')
                die = partitioned_dice[2]
                amount = int(partitioned_dice[0])

                if amount > 100 or int(die[-1]) > 99:
                    await ctx.send("Oversized dice roll.")
                    return

            else:
                die = roll

            try:
                r, e = rolldice.roll_dice(die)
            except Exception:
                await ctx.send("Invalid or oversized dice roll.")
                return

            display = str(F"""```css\n{r}```""")
            embed = discord.Embed(title=f":game_die: Dicebag: {name}")
            embed.add_field(name=f"{dicebags[name]}: {e}", value=display)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Dicebag(client))
