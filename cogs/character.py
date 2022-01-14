import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
import modules.dnd as dd
import modules.utility as u
import rolldice as rd
import json
from json import JSONEncoder
from pymongo import MongoClient


with open("data/config.json") as f:
    setup = json.load(f)

# Connect to the database and load the character collection.
client = MongoClient(setup['connection_string'])
db = client.SiriusDB
collection = db.characters


class Characters(commands.Cog):
    """Handles character creation, storage and interaction on multiple game
    systems."""
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="newcharacter",
                       description="Create a new character (up to 10 per "
                                   "account). Character class and level "
                                   "are optional.",
                       options=[
                        create_option(
                            name="system",
                            description="Game system for the character sheet.",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(name="Call of Cthulhu 7e",
                                              value="Call of Cthulhu 7e"),
                                create_choice(name="D&D 5e", value="D&D 5e"),
                                create_choice(name="Fate Core",
                                              value="Fate Core"),
                                create_choice(name="Pathfinder 2e",
                                              value="Pathfinder 2e")
                            ]),
                        create_option(
                            name="character_name",
                            description="Character name.",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="character_class",
                            description="Character class. Only used if "
                                        "supported by the selected system.",
                            option_type=3,
                            required=False
                        ),
                        create_option(
                            name="character_level",
                            description="Character level. Only used if "
                                        "supported by the selected system.",
                            option_type=4,
                            required=False
                        )])
    async def newcharacter(self, ctx, system, character_name,
                           character_class="", character_level=""):
        """Creates a new character and appends it to the user's key on the
        database. Can receive a character name, class and level as input.
        Each account may have up to 10 characters at a time."""
        if system == "D&D 5e":
            from modules.dnd5e_character import DnD5e_Character
            # Set generic properties.
            if not character_class:
                character_class = "fighter"
            if not character_level:
                character_level = 1

            char = DnD5e_Character(character_name, character_class,
                                   character_level),

        elif system == "Fate Core":
            from modules.fatecore_character import FateCore_Character
            char = FateCore_Character(character_name)

        elif system == "Call of Cthulhu 7e":
            from modules.coc7e_character import CallOfCthulhu_Character
            char = CallOfCthulhu_Character(character_name)

        elif system == "Pathfinder 2e":
            if not character_class:
                character_class = "fighter"
            if not character_level:
                character_level = 1
            from modules.pathfinder2e_character import Pathfinder2e_Character
            char = Pathfinder2e_Character(character_name, character_class,
                                          character_level)

        char = json.loads(CharacterEncoder().encode(char))
        query = {"_id": ctx.author.id}
        results = collection.find_one(query)
        counter = 0

        # The encoder can either return a list or the dictionary itself.
        if type(char) == list:
            for i in char:
                char = i

        if results:
            for result in results:
                counter += 1

            if character_name in results:
                await ctx.send("Character name unavailable.")
                return

        if counter != 0:
            # Updates the database for an already existing user.
            if counter >= 11:
                await ctx.send("You may only have up to 10 characters at a "
                               "time.")
                return

            collection.update_one({"_id": ctx.author.id},
                                  {"$set": {character_name: char}})

        else:
            # Adds a new user to the database.
            collection.insert_one({"_id": ctx.author.id, character_name: char})

        await ctx.send("Character created successfully.")

    @cog_ext.cog_slash(name="deletecharacter",
                       description="Delete an existing character.",
                       options=[
                        create_option(
                            name="character_name",
                            description="Name of the character to be deleted.",
                            option_type=3,
                            required=True
                        )])
    async def deletecharacter(self, ctx, character_name):
        """Displays a confirmation prompt and removes the specified character
        from the database upon confirmation. Has a 30s timeout."""

        query = {"_id": ctx.author.id}
        results = collection.find(query)
        characters = []

        for result in results:
            for i in result:
                characters.append(i)

        if character_name not in characters:
            await ctx.send("Character not found.")
            return

        await ctx.send((f"'{character_name}' will be deleted. This process is "
                        "irreversible. Do you confirm? (y/n)"))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and\
                msg.content.lower() in ['y', 'n']

        try:
            msg = await self.client.wait_for("message", check=check,
                                             timeout=30)

            if msg.content.lower() == 'y':
                collection.update_one({"_id": ctx.author.id},
                                      {"$unset": {character_name: 1}})

                await ctx.send("Character deleted successfully.")
                return

            else:
                await ctx.send("Character deletion cancelled.")
                return

        except Exception:
            await ctx.send("Request timed out after 30 seconds.")
            return

    @cog_ext.cog_slash(name="listcharacters",
                       description="Displays all your characters.")
    async def listcharacters(self, ctx):
        """Loops through a user's characters on the database and lists all
        existing items on an embed."""

        query = {"_id": ctx.author.id}
        results = collection.find_one(query)
        characters = []
        embed = discord.Embed(title=f"{str(ctx.author)[:-5]}'s Character List")

        if results:
            for i in results:
                if i != "_id":
                    def f(a):
                        return f"{u.adjust_length(str(results[i][a]), 100)}" \
                            if results[i][a] else 'undefined'

                    embed.add_field(name=i,
                                    value=(f"System: {f('system')}\n"
                                           f"Description: {f('description')}"),
                                    inline=False)
                    characters.append(i)

        if len(characters) > 0:
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send("Character list is empty.")
            return

    @cog_ext.cog_slash(name="character",
                       description="Displays character sheets, roll attributes"
                                   " and edit an existing character's "
                                   "information.",
                       options=[
                        create_option(
                            name="character_name",
                            description="Character name.",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="command",
                            description="Command to be executed. Ommit to "
                                        "display the character sheet.",
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="set", value="set"),
                                create_choice(name="add", value="add"),
                                create_choice(name="remove", value="remove"),
                                create_choice(name="roll", value="roll"),
                                create_choice(name="level_up",
                                              value="level_up"),
                                create_choice(name="show_inventory",
                                              value="inventory")
                            ]),
                        create_option(
                            name="attribute",
                            description="Character attribute for command "
                                        "execution. Only required if command"
                                        " is set, roll, add or remove.",
                            option_type=3,
                            required=False
                        ),
                        create_option(
                            name="value",
                            description="New value for character attribute. "
                                        "Only required if command is set or "
                                        "add.",
                            option_type=3,
                            required=False
                        )])
    async def character(self, ctx, character_name="", command="", attribute="",
                        value=""):
        """Displays and handles character information and commands."""
        player = f"<@{ctx.author.id}>"
        query = {"_id": ctx.author.id}

        try:
            char = collection.find_one(query)[character_name]
        except Exception:
            await ctx.send("Character not found.")
            return

        # Spaces, underscores and hyphens work as attribute separators.
        attribute = attribute.replace('-', '_').lower()
        attribute = attribute.replace(" ", "_")

        if attribute == "class":
            # To avoid conflict with Python's classes.
            attribute = "cclass"

        if command:
            if command == 'inventory':
                # Universal character inventory for all game systems.
                if len(char['inventory']) < 65:
                    inventory = u.adjust_length(char['inventory'].ljust(65),
                                                4080)
                else:
                    inventory = u.adjust_length(char['inventory'], 4080)

                embed = discord.Embed(title=f"{char['name']}'s Inventory",
                                      description=(f"**Contents:**\n"
                                                   f"{inventory}"))
                embed.add_field(name="Currency:", value=char['currency'])
                await ctx.send(embed=embed)

            elif command == "add":
                if "additional_skill" in attribute and "name" in attribute:
                    if len(value) > 20:
                        await ctx.send("Item exceeds field's maximum "
                                       "character length.")
                        return

                if (type(char[attribute]) == int or
                        char[attribute].isnumeric()):
                    # If the attribute is a number, sum attribute and value.
                    char[attribute] = int(char[attribute]) + int(value)

                elif type(char[attribute]) == str and len(char[attribute]) > 0:
                    # If the attribute is a string, append value the end of it
                    # with a comma.
                    char[attribute] += f", {value}"
                    if len(char[attribute]) > 300:
                        await ctx.send("Field exceeds 300 character "
                                       "limit.")
                        return

                else:
                    # If the field is empty, make it value.
                    char[attribute] = value

                collection.update_one({"_id": ctx.author.id}, {"$set":
                                      {character_name: char}})

                await ctx.send("Character attribute updated succesfully.")
                return

            elif command == 'remove':
                try:
                    if (type(char[attribute]) == int or
                        # If the attribute is a number, subtract value from it.
                       char[attribute].isnumeric()):
                        char[attribute] = int(char[attribute]) - int(value)

                    elif type(char[attribute]) == str:
                        # If attribute is a string, remove value from it.
                        # Accounts for all value positions in an attribute
                        # string.
                        char[attribute] = char[attribute].replace(f', {value}',
                                                                  '')
                        char[attribute] = char[attribute].replace(f'{value}, ',
                                                                  '')
                        char[attribute] = char[attribute].replace(value, '')

                    collection.update_one({"_id": ctx.author.id}, {"$set":
                                          {character_name: char}})

                    await ctx.send("Character attribute updated successfully.")
                    return

                except Exception:
                    await ctx.send("Value not found in character attribute.")
                    return

            elif command == "set":
                # Some parameters are handled separately to account for their
                # specific needs.
                if attribute == "name":
                    if len(value) <= 25:
                        char[attribute] = value

                        collection.update_one({"_id": ctx.author.id},
                                              {"$set": {character_name: char}})
                        collection.update_one({"_id": ctx.author.id},
                                              {"$rename":
                                              {character_name: value}})

                    await ctx.send("Character name updated successfully.")
                    return

                elif attribute == "image":
                    # The image URL is verified by sending a response embed. If
                    # the message is successfully sent, it is considered valid
                    # and the URL gets saved to the character sheet.
                    try:
                        embed = discord.Embed(title="Character image updated "
                                                    "successfully.")
                        embed.set_image(url=value)

                        char['image'] = value

                        collection.update_one({"_id": ctx.author.id},
                                              {"$set": {character_name: char}})

                        await ctx.send(embed=embed)
                        return

                    except Exception:
                        await ctx.send("Invalid image URL.")
                        return

                elif attribute == "level":
                    # Makes corresponding changes to experience in accordance
                    # to the game system.
                    char['level'] = int(value)

                    if char['system'] == "D&D 5e":
                        if int(value) > 20:
                            await ctx.send("Character level cannot be higher"
                                           " than 20.")
                            return
                        else:
                            experience = dd.get_experience(int(value))

                            char['experience'] = int(experience)
                            char['level'] = int(value)
                            char['hit_dice'] = char['level']

                    collection.update_one({"_id": ctx.author.id}, {"$set":
                                          {character_name: char}})

                    await ctx.send("Character attribute updated successfully.")
                    return

                elif attribute == "experience":
                    char['experience'] = int(value)

                    if char['system'] == "D&D 5e":
                        char['level'] = dd.get_level(int(value))
                        char['hit_dice'] = char['level']
                    elif char['system'] == "Pathfinder 2e":
                        if int(value) == 1000:
                            char['level'] += 1
                            char['experience'] = 0
                        elif int(value) > 1000:
                            char['level'] += int(int(value)/1000)
                            char['experience'] -= 1000

                    collection.update_one({"_id": ctx.author.id},
                                          {"$set": {character_name: char}})

                    await ctx.send("Character attribute updated "
                                   "successfully.")
                    return

                elif attribute == "cclass":
                    if len(value) <= 20:
                        if char['system'] == "D&D 5e":
                            char['saving_throws'] = \
                                dd.get_saving_throws(value,
                                                     char['saving_throws'])
                            char['hit_die'] = \
                                dd.get_hit_die(value, char['hit_dice'])

                        collection.update_one({"_id": ctx.author.id}, {"$set":
                                              {character_name: char}})

                    await ctx.send("Character attribute updated "
                                   "successfully.")
                    return

                elif attribute == "description":
                    # Description has a higher maximum allowed length than
                    # other fields.
                    if len(value) <= 3000:
                        char['description'] = str(value)
                        collection.update_one({"_id": ctx.author.id},
                                              {"$set":
                                              {character_name: char}})
                        await ctx.send("Character attribute updated "
                                       "successfully.")
                        return
                    else:
                        await ctx.send("Character descriptions may only have "
                                       "up to 3000 characters.")
                        return

                elif "additional_skill" in attribute and "name" in attribute:
                    if len(value) > 20:
                        await ctx.send("Item exceeds field's maximum "
                                       "character length.")
                        return

                if attribute in char:
                    # Handles generic attribute modifications. Value returns as
                    # a string, so booleans and integers need to be addressed
                    # separately.
                    if value.isnumeric():
                        value = int(value)

                    elif value == "True":
                        value = True

                    elif value == "False":
                        value = False

                    elif len(value) > 1000:
                        await ctx.send("Item exceeds field's maximum character"
                                       " length.")
                        return

                    char[attribute] = value

                    collection.update_one({"_id": ctx.author.id},
                                          {"$set":
                                          {character_name: char}})

                    await ctx.send("Character attribute updated successfully.")
                    return

                else:
                    await ctx.send(f"Character attribute ''{attribute}'' not "
                                   "found.")
                    return

            elif command == 'level_up':
                # Changes character level, experience and other system-specific
                # attributes.
                char['level'] = char['level'] + 1

                if char['system'] == "D&D 5e":
                    if char['level'] == 20:
                        await ctx.send("Character is already at the maximum "
                                       "supported level.")
                        return

                    char['hit_dice'] = char['level']
                    char['experience'] = dd.get_experience(char['level'])

                elif char['system'] == "Pathfinder 2e":
                    if char['level'] == 20:
                        await ctx.send("Character is already at the maximum "
                                       "supported level.")
                        return
                    char['experience'] = 0

                collection.update_one({"_id": ctx.author.id}, {"$set":
                                      {character_name: char}})

                await ctx.send("Character level updated successfully.")
                return

            elif command == 'roll':
                # Rolls attribute in accordance to game system rules.
                try:
                    if (char['system'] == "D&D 5e" or
                            char['system'] == "Pathfinder 2e"):
                        if attribute in ['strength', 'dexterity',
                                         'constitituion', 'wisdom',
                                         'intelligence', 'charisma']:

                            mod = int(dd.get_modifier(int(char[attribute])))
                            res, exp = rd.roll_dice(f"1d20 + {mod}")

                        elif attribute == "death_save":
                            res, exp = rd.roll_dice("1d20")
                            display = "Death Save"

                            if res >= 10:
                                char["death_saves_successes"] += 1
                            else:
                                char["death_saves_failures"] += 1
                            collection.update_one({"_id": ctx.author.id}, {
                                                  "$set": {character_name:
                                                           char}})
                        else:
                            res, exp = rd.roll_dice("1d20 + "
                                                    f"{char[attribute]}")

                    elif char['system'] == "Call of Cthulhu 7e":
                        res, exp = rd.roll_dice("1d100")

                        if res == 100:
                            res = f"{res} FUMBLE"
                        elif res >= char[attribute] and res != 100:
                            res = f"{res} FAIL"
                        elif (res <= char[attribute] and res > char[attribute]
                              / 2):
                            res = f"{res} SUCCESS"
                        elif (res <= char[attribute]/2 and res >
                              char[attribute]/5):
                            res = f"{res} HARD SUCCESS"
                        elif res <= char[attribute]/5:
                            res = f"{res} EXTREME SUCCESS"

                    else:
                        # Generic attribute roll.
                        res, exp = rd.roll_dice(f"1d20 + {char[attribute]}")

                    display = attribute.title().replace("_", " ")
                    embed = discord.Embed(title=f"🎲 {char['name']}: {display}")
                    embed.add_field(name=exp, value=(f"""```css\n{res}```"""))

                    await ctx.send(embed=embed)
                    return

                except Exception:
                    await ctx.send(f"Character attribute {attribute} cannot be"
                                   " rolled.")
                    return
        else:
            # If no command is used, all character sheet pages are generated.
            # The first page is returned and emote reactions are added to it,
            # allowing user input for navigation.
            try:
                if char['system'] == "D&D 5e":
                    from modules.dnd5e_character import DnD5e_Character
                    page_1 = DnD5e_Character.make_page_1(char, player)
                    page_2 = DnD5e_Character.make_page_2(char)
                    page_3 = DnD5e_Character.make_page_3(char)
                    pages = [page_1, page_2, page_3]

                elif char['system'] == "Fate Core":
                    from modules.fatecore_character import FateCore_Character
                    page_1 = FateCore_Character.make_page_1(char, player)
                    pages = [page_1]

                elif char['system'] == "Call of Cthulhu 7e":
                    from modules.coc7e_character import CallOfCthulhu_Character
                    page_1 = CallOfCthulhu_Character.make_page_1(char, player)
                    page_2 = CallOfCthulhu_Character.make_page_2(char, player)
                    pages = [page_1, page_2]

                elif char['system'] == "Pathfinder 2e":
                    from modules.pathfinder2e_character import \
                        Pathfinder2e_Character
                    page_1 = Pathfinder2e_Character.make_page_1(char, player)
                    page_2 = Pathfinder2e_Character.make_page_2(char, player)
                    page_3 = Pathfinder2e_Character.make_page_3(char, player)

                    pages = [page_1, page_2, page_3]

                message = await ctx.send(embed=page_1)

            except Exception:
                await ctx.send("Character sheet build has failed.")
                return

        message_id = message.id

        await message.add_reaction('◀')
        await message.add_reaction('▶')

        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None
        user = None

        while True:
            if reaction is not None and reaction.message.id == message_id:
                if str(reaction) == '◀':
                    # Previous page in character sheet.
                    if i >= 0:
                        i -= 1
                        new_page = pages[i]
                        await message.edit(embed=new_page)

                    else:
                        i = len(pages) - 1
                        new_page = pages[i]
                        await message.edit(embed=new_page)

                elif str(reaction) == '▶':
                    # Next page in character sheet.
                    if i < len(pages) - 1:
                        i += 1
                        new_page = pages[i]
                        await message.edit(embed=new_page)

                    else:
                        i = 0
                        new_page = pages[i]
                        await message.edit(embed=new_page)

            try:
                reaction, user = await self.client.wait_for('reaction_add',
                                                            timeout=60.0,
                                                            check=check)
                await message.remove_reaction(reaction, user)
            except Exception:
                break

        await message.clear_reactions()


class CharacterEncoder(JSONEncoder):
    """Makes character instances JSON serializable for database storage."""
    def default(self, o):
        return o.__dict__


def setup(client):
    client.add_cog(Characters(client))
