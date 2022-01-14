import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import aiofiles
import os
import urllib.request
from pymongo import MongoClient
import json


with open("data/config.json") as f:
    setup = json.load(f)

# Connect to the database and load the character collection.
client = MongoClient(setup['connection_string'])
db = client.SiriusDB
collection = db.battlemaps


# Color options for grid, numbers and shapes.
colors = {
    'red': (192, 57, 43),
    'green': (39, 174, 96),
    'blue': (41, 128, 185),
    'cyan': (52, 152, 219),
    'yellow': (241, 196, 15),
    'orange': (230, 126, 34),
    'purple': (142, 68, 173),
    'violet': (155, 89, 182),
    'white': (255, 255, 255),
    'grey': (127, 140, 141),
    'gray': (127, 140, 141),
    'black': (0, 0, 0)
}


class Battlemap(commands.Cog):
    """Handles battlemap creation and interactions."""
    def __init__(self, client):
        self.client = client

    def optimize_image(self, im, channel, size, counter, counter1):
        """Crops based on grid size, resizes accordingly, converts and
        optimizes an image for storage."""
        im = im.crop(box=(0, 0, int(size*(counter-1)),
                     int(size*(counter1-1))))
        im = im.resize((im.width, im.height), resample=1)
        im = im.convert('RGB')
        im.save(f"data/images/{channel}.JPEG", quality=65, optimize=True)

    async def plot(self, channel, url, size, color, line_width):
        """Requests image from the URL argument, plots a grid on top of it and
        saves it as a JPEG with the battlemap channel ID."""
        # Save file from URL.
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f'data/images/{channel}.JPEG',
                                            mode='wb')
                    await f.write(await resp.read())
                    await f.close()

        im = Image.open(f"data/images/{channel}.JPEG")
        draw = ImageDraw.Draw(im)
        # Numbers are half the size of the square sides.
        font = ImageFont.truetype("data/arial.ttf", int(float(size) * 0.5))
        width = im.width
        height = im.height
        square_size = int(size)
        counter = 0
        counter1 = 0

        for x in range(0, width, square_size):
            line = ((x, 0), (x, height))
            draw.line(line, fill=colors[color], width=line_width)
            text = (x, 0)

            draw.text(text, text=str(counter), font=font, fill=colors[color],
                      width=line_width)
            counter += 1

        for y in range(0, height, square_size):
            line = ((0, y), (width, y))
            draw.line(line, fill=colors[color], width=line_width)

            text = (0, y)
            draw.text(text, text=str(counter1), font=font, fill=colors[color],
                      width=line_width)
            counter1 += 1

        del draw

        await self.client.loop.run_in_executor(None, self.optimize_image,
                                               im, channel, square_size,
                                               counter, counter1)

    def assemble(self, battlemap, channel):
        """Plots all tokens and shapes on their corresponding battlemap and
        temporarily saves the image as a PNG."""
        im = Image.open(f"data/images/{channel}.JPEG")
        im = im.convert("RGBA")
        overlay = Image.new('RGBA', im.size)
        draw = ImageDraw.Draw(overlay)
        obj = Image.new('RGBA', im.size)
        obj.putalpha(0)
        layers = battlemap['layers']
        # the layer on top needs to be plotted last, so the list should be
        # reversed.
        layers.reverse()

        for i in layers:
            x = battlemap['tokens'][i]['x']
            y = battlemap['tokens'][i]['y']
            xsize = battlemap['tokens'][i]['xsize']
            ysize = battlemap['tokens'][i]['ysize']

            if 'shape' in battlemap['tokens'][i]:
                shape = battlemap['tokens'][i]['shape']
                width = battlemap['tokens'][i]['width']
                opacity = battlemap['tokens'][i]['opacity']
                color = list(colors[battlemap['tokens'][i]['color']])
                # opacity is appended as the alpha channel value
                color.append(opacity)
                color = tuple(color)
                fill = bool(battlemap['tokens'][i]['fill'])

                if shape == 'ellipse':
                    if fill:
                        draw.ellipse((x, y, x+xsize, y+ysize), outline=color,
                                     fill=color, width=width)
                    else:
                        draw.ellipse((x, y, x+xsize, y+ysize), outline=color,
                                     width=width)

                elif shape == 'rectangle':
                    if fill:
                        draw.rectangle((x, y, x+xsize, y+ysize), outline=color,
                                       fill=color, width=width)
                    else:
                        draw.rectangle((x, y, x+xsize, y+ysize), outline=color,
                                       width=width)

            else:
                url = battlemap['tokens'][i]['url']
                path = f'data/images/{i}.PNG'

                try:
                    urllib.request.urlretrieve(url, path)

                    tk = Image.open(path)
                    tk = tk.convert('RGBA')
                    tk = tk.resize((xsize, ysize), Image.ANTIALIAS)
                    tk = tk.crop(tk.getbbox())
                    # avoids layer conflicts between shapes and tokens
                    overlay.paste(tk, (x, y), tk)
                    os.remove(path)

                except Exception:  # skip unavailable URLs
                    pass

        # Blends token and shape layers and adds an alpha channel for
        # transparency.
        im = Image.alpha_composite(im, overlay)

        im.save(f"data/images/{channel}.PNG", format="PNG")

    @commands.Cog.listener()
    async def on_guild_channel_delete(ctx, channel):
        query = {"_id": channel.id}
        results = collection.find_one(query)

        if results:
            collection.delete_one(query)
            os.remove(f"data/images/{channel.id}.JPEG")

    @cog_ext.cog_slash(name="battlemap",
                       description="Displays the currently active battlemap.")
    async def battlemap(self, ctx):
        """Calls for assembly and returns the currently active battlemap on the
        command execution channel."""
        channel = ctx.channel.id
        path = f'data/images/{channel}.PNG'
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        msg = await ctx.send("Processing image...")

        import time
        t1 = time.time()
        await self.client.loop.run_in_executor(None, self.assemble, battlemap,
                                               channel)
        t2 = time.time()
        print(t2-t1)
        discord_file = discord.File(path)

        await msg.edit(file=discord_file)
        os.remove(path)

    @cog_ext.cog_slash(name="newbattlemap",
                       description=("Creates a new battlemap attached to the "
                                    "current channel."),
                       options=[
                        create_option(
                            name="url",
                            description=("Battlemap image URL."),
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="size",
                            description=("Square size for the battlemap "
                                         "grid."),
                            option_type=4,
                            required=True
                        ),
                        create_option(
                            name="color",
                            description="Color for the battlemap grid.",
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="red", value="red"),
                                create_choice(name="green", value="green"),
                                create_choice(name="blue", value="blue"),
                                create_choice(name="cyan", value="cyan"),
                                create_choice(name="yellow", value="yellow"),
                                create_choice(name="orange", value="orange"),
                                create_choice(name="purple", value="purple"),
                                create_choice(name="violet", value="violet"),
                                create_choice(name="white", value="white"),
                                create_choice(name="gray", value="gray"),
                                create_choice(name="black", value="black")
                            ]),
                        create_option(
                            name="line_width",
                            description="Line width for battlemap grid.",
                            option_type=4,
                            required=False
                        )])
    async def newbattlemap(self, ctx, url, size, color='black', line_width=1):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            await ctx.send("This channel already has an active battlemap.")
            return

        if color not in colors:
            await ctx.send("Invalid color.")
            return

        elif line_width <= 0 or line_width > 50:
            line_width = 1

        msg = await ctx.send("Processing image...")
        await self.plot(channel, url, size, color, int(line_width))

        discord_file = discord.File(f"data/images/{channel}.JPEG")

        structure = {"author": author, "size": int(size), "layers": [],
                     "tokens": {}, "editors": []}

        collection.insert_one({"_id": channel, "battlemap": structure})

        await ctx.send(file=discord_file)
        await msg.edit(content="Battlemap created successfully.")

    @cog_ext.cog_slash(name="deletebattlemap",
                       description="Deletes the currently active battlemap.")
    async def deletebattlemap(self, ctx):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if "battlemap" not in results:
            await ctx.send("This channel has no active battlemap.")
            return

        elif (author != results['battlemap']['author'] and not
              ctx.author.guild_permissions.administrator):
            await ctx.send("Only battlemap authors and server administrators "
                           "can delete battlemaps.")
            return

        await ctx.send("Currently active battlemap will be deleted. This "
                       "process is irreversible. Do you wish to proceed? "
                       "(y/n)")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and\
                msg.content.lower() in ['y', 'n']

        msg = await self.client.wait_for("message", check=check, timeout=30)

        if msg.content.lower() == 'y':
            collection.delete_one(query)
            os.remove(f"data/images/{ctx.channel.id}.JPEG")

            await ctx.send("Battlemap deleted successfully.")

        else:
            await ctx.send("Battlemap deletion cancelled.")

    @cog_ext.cog_slash(name="listtokens",
                       description="Lists all tokens in the active battlemap.")
    async def listtokens(self, ctx):
        channel = ctx.channel.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        size = battlemap['size']
        tokens = battlemap['tokens']
        embed = discord.Embed(title=f'Tokens on #{ctx.channel}')

        if len(tokens) == 0:
            embed.add_field(name="This battlemap has no tokens.",
                            value="Add a token with the addtoken command.")

        for i in tokens:
            if 'shape' in tokens[i]:
                shape = tokens[i]['shape']
                width = tokens[i]['width']
                color = tokens[i]['color']
                x = int(tokens[i]['x'] / size)
                y = int(tokens[i]['y'] / size)

                embed.add_field(name=i, value=(f"**Shape:** {shape}\n **Width:"
                                               f"** {width}\n**Color:** "
                                               f" {color}\n**X:** {x}\n**Y:** "
                                               f"{y}"))

            else:
                url = tokens[i]['url']
                x = int(tokens[i]['x'] / size)
                y = int(tokens[i]['y'] / size)

                embed.add_field(name=i, value=(f"**URL:** {url}\n**X:** {x}\n"
                                               f"**Y:** {y}"))

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="addtoken",
                       description="Adds a token to the active battlemap.",
                       options=[
                           create_option(
                               name="name",
                               description="Token name.",
                               option_type=3,
                               required=True
                           ),
                           create_option(
                               name="url",
                               description="URL for the token image.",
                               option_type=3,
                               required=True
                           ),
                           create_option(
                               name="x",
                               description="Token X coordinate.",
                               option_type=4,
                               required=False
                           ),
                           create_option(
                               name="y",
                               description="Token Y coordinate.",
                               option_type=4,
                               required=False
                           ),
                           create_option(
                               name="xsize",
                               description="Token X size.",
                               option_type=4,
                               required=False
                           ),
                           create_option(
                               name="ysize",
                               description="Token Y size.",
                               option_type=4,
                               required=False
                           )])
    async def addtoken(self, ctx, name, url, x=0, y=0, xsize=1, ysize=1):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if len(battlemap['tokens']) >= 30:
            await ctx.send("Battlemaps may have no more than 30 tokens.")
            return

        elif (author != battlemap['author'] and
              author not in battlemap['editors'] and not
              ctx.author.guild_permissions.administrator):
            await ctx.send("You do not have the permissions required to "
                           "execute this command.")
            return

        elif (int(xsize) <= 0 or int(xsize) > 10 or int(ysize) <= 0 or
              int(ysize) > 10):
            await ctx.send("Invalid size.")
            return

        elif name in battlemap['tokens']:
            await ctx.send("Token name unavailable.")
            return

        x = x * battlemap['size']
        y = y * battlemap['size']
        xsize = int(xsize * battlemap['size'])
        ysize = int(ysize * battlemap['size'])

        battlemap['tokens'].update({name: {'url': url, 'x': x, 'y': y,
                                           'xsize': xsize, 'ysize': ysize}})
        battlemap['layers'].insert(0, name)

        collection.update_one({"_id": channel}, {"$set":
                              {"battlemap": battlemap}})

        await ctx.send("Token added sucessfully.")

    @cog_ext.cog_slash(name="deletetoken",
                       description=("Deletes a token from the active "
                                    "battlemap."),
                       options=[
                           create_option(
                               name="name",
                               description="Token name.",
                               option_type=3,
                               required=True
                           )])
    async def deletetoken(self, ctx, name):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if (author != battlemap['author'] and
            author not in battlemap['editors'] and not
                ctx.author.guild_permissions.administrator):
            await ctx.send("You do not have the permissions required to "
                           "execute this command.")
            return

        elif name not in battlemap['tokens']:
            await ctx.send("Token not found.")
            return

        del(battlemap['tokens'][name])
        battlemap['layers'].remove(name)
        collection.update_one({"_id": channel}, {"$set":
                              {"battlemap": battlemap}})

        await ctx.send("Token removed sucessfully.")

    @cog_ext.cog_slash(name="movetoken",
                       description=("Moves a token from the active "
                                    "battlemap."),
                       options=[
                            create_option(
                                name="name",
                                description="Token name.",
                                option_type=3,
                                required=True
                            ),
                            create_option(
                                name="x",
                                description="New X-coordinate.",
                                option_type=4,
                                required=True
                            ),
                            create_option(
                                name="y",
                                description="New Y-coordinate.",
                                option_type=4,
                                required=True
                            )])
    async def movetoken(self, ctx, name, x=None, y=None):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)
        msg = await ctx.send("Processing image...")

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if name not in battlemap['tokens']:
            await ctx.send("Token not found.")
            return

        elif (author != battlemap['author'] and
              author not in battlemap['editors'] and not
              ctx.author.guild_permissions.administrator):
            await ctx.send("You do not have the permissions required to "
                           "execute this command.")
            return

        if x:
            x = int(x) * battlemap['size']
            battlemap['tokens'][name]['x'] = x
        if y:
            y = int(y) * battlemap['size']
            battlemap['tokens'][name]['y'] = y

        collection.update_one({"_id": channel}, {"$set":
                              {"battlemap": battlemap}})

        await self.client.loop.run_in_executor(None, self.assemble, battlemap,
                                               channel)

        path = f'data/images/{channel}.PNG'
        discord_file = discord.File(path)

        await msg.edit(file=discord_file)
        os.remove(path)

    @cog_ext.cog_slash(name="newshape",
                       description=("Adds a shape to the active battlemap."),
                       options=[
                        create_option(
                            name="name",
                            description="Shape alias for commands.",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="shape",
                            description="Type of shape.",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(name="rectangle",
                                              value="rectangle"),
                                create_choice(name="ellipse", value="ellipse")
                            ]
                        ),
                        create_option(
                            name="width",
                            description="Shape line width.",
                            option_type=4,
                            required=False
                        ),
                        create_option(
                            name="color",
                            description="Shape color.",
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="red", value="red"),
                                create_choice(name="green", value="green"),
                                create_choice(name="blue", value="blue"),
                                create_choice(name="cyan", value="cyan"),
                                create_choice(name="yellow", value="yellow"),
                                create_choice(name="orange", value="orange"),
                                create_choice(name="purple", value="purple"),
                                create_choice(name="violet", value="violet"),
                                create_choice(name="white", value="white"),
                                create_choice(name="gray", value="gray"),
                                create_choice(name="black", value="black")
                            ]
                        ),
                        create_option(
                            name="fill",
                            description=("Whether or not the shape should be "
                                         "filled."),
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="True", value="True"),
                                create_choice(name="False", value="False")
                            ]
                        ),
                        create_option(
                            name="x",
                            description="Token X coordinate.",
                            option_type=4,
                            required=False
                        ),
                        create_option(
                            name="y",
                            description="Token Y coordinate.",
                            option_type=4,
                            required=False
                        ),
                        create_option(
                            name="xsize",
                            description="Token X size.",
                            option_type=4,
                            required=False
                        ),
                        create_option(
                            name="ysize",
                            description="Token Y size.",
                            option_type=4,
                            required=False
                        )])
    async def newshape(self, ctx, name, shape, width=1, color='black',
                       fill=True, x=0, y=0, xsize=1, ysize=1, opacity=100):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if (int(xsize) <= 0 or int(xsize) > 10 or int(ysize) <= 0 or
           int(ysize) > 10):
            await ctx.send("Invalid size.")
            return

        elif width <= 0 or width > 10:
            await ctx.send("Invalid line width.")
            return

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if (author != battlemap['author'] and
            author not in battlemap['editors'] and not
                ctx.author.guild_permissions.administrator):
            await ctx.send("You do not have the permissions required to "
                           "execute this command.")
            return

        elif len(battlemap['tokens']) >= 30:
            await ctx.send("Battlemaps may have no more than 30 tokens.")
            return

        elif name in battlemap['tokens']:
            await ctx.send("Token name unavailable.")
            return

        x = int(x * battlemap['size'])
        y = int(y * battlemap['size'])
        xsize = int(xsize * battlemap['size'])
        ysize = int(ysize * battlemap['size'])
        opacity = round(2.56 * opacity)  # transform from percentage

        structure = {name: {'shape': shape, 'width': width, 'color': color,
                            'fill': fill, 'x': x, 'y': y, 'xsize': xsize,
                            'ysize': ysize, 'opacity': opacity}}

        battlemap['tokens'].update(structure)
        battlemap['layers'].insert(0, name)

        collection.update_one({"_id": channel}, {"$set":
                              {"battlemap": battlemap}})

        await ctx.send("Shape created successfully.")

    @cog_ext.cog_slash(name="layers",
                       description="Manages token layers.",
                       options=[
                            create_option(
                                name="name",
                                description="Token name.",
                                option_type=3,
                                required=True
                            ),
                            create_option(
                                name="command",
                                description="Command to be executed on token.",
                                option_type=3,
                                required=True,
                                choices=[
                                    create_choice(name="forward",
                                                  value="forward"),
                                    create_choice(name="to_front",
                                                  value="to_front"),
                                    create_choice(name="backward",
                                                  value="backward"),
                                    create_choice(name="to_back",
                                                  value="to_back"),
                                ]
                            )])
    async def layers(self, ctx, name, command):
        channel = ctx.channel.id
        author = ctx.author.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if (author != battlemap['author'] and
            author not in battlemap['editors'] and not
                ctx.author.guild_permissions.administrator):
            await ctx.send("You do not have the permissions required to "
                           "execute this command.")
            return

        elif name not in battlemap['tokens']:
            await ctx.send("Invalid token.")
            return

        layers = battlemap['layers']
        index = layers.index(name)
        layers.remove(name)

        if command == "forward":
            index -= 1

        elif command == "to_front":
            index = 0

        elif command == 'backward':
            index += 1

        elif command == 'to_back':
            index = len(layers)

        layers.insert(index, name)
        battlemap['layers'] = layers

        collection.update_one({"_id": channel}, {"$set":
                              {"battlemap": battlemap}})

        await self.client.loop.run_in_executor(None, self.assemble, battlemap,
                                               channel)

        path = f'data/images/{channel}.PNG'
        discord_file = discord.File(path)

        await ctx.send(file=discord_file)
        os.remove(path)

    @cog_ext.cog_slash(name="addeditor",
                       description=("Give a user editor permissions on the "
                                    "active battlemap."),
                       options=[
                           create_option(
                               name="user",
                               description="User to be added as an editor.",
                               option_type=6,
                               required=True
                           )])
    async def addeditor(self, ctx, user):
        channel = ctx.channel.id
        author = ctx.author.id
        user_id = user.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if (author != battlemap['author'] and not
                ctx.author.guild_permissions.administrator):
            await ctx.send("Only battlemap authors and server administrators "
                           "can give users editor permissions.")
            return

        elif user.bot:
            await ctx.send("A bot cannot be added as an editor.")
            return

        elif user_id in battlemap['editors']:
            await ctx.send(f"{user} is already an editor.")
            return

        elif user_id == battlemap['author']:
            await ctx.send(f"{user} is the author of the currently active "
                           "battlemap.")
            return

        editors = battlemap['editors']
        editors.insert(0, user_id)
        battlemap['editors'] = editors

        collection.update_one({"_id": channel}, {"$set":
                              {"battlemap": battlemap}})

        await ctx.send(f"<@{user_id}> has been added to the editor list "
                       "successfully.")

    @cog_ext.cog_slash(name="removeeditor",
                       description=("Revoke a user's editor permissions on "
                                    "the active battlemap."),
                       options=[
                           create_option(
                               name="user",
                               description=("User to be removed from the "
                                            "editor list."),
                               option_type=6,
                               required=True
                           )])
    async def removeeditor(self, ctx, user):
        channel = ctx.channel.id
        author = ctx.author.id
        user_id = user.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        if (author != battlemap['author'] and not
                ctx.author.guild_permissions.administrator):
            await ctx.send("Only battlemap authors and server administrators "
                           "can revoke users' editor permissions.")
            return

        elif user_id not in battlemap['editors']:
            await ctx.send("The selected user does not have editor "
                           "permissions on the active battlemap.")
            return

        editors = battlemap['editors']
        editors.remove(user_id)
        battlemap['editors'] = editors

        collection.update_one({"_id": channel}, {"$set": {"battlemap":
                                                          battlemap}})

        await ctx.send(f"Editor permissions revoked from <@{user_id}> "
                       "successfully.")

    @cog_ext.cog_slash(name="listeditors",
                       description="Display active battlemap's editor list")
    async def listeditors(self, ctx):
        channel = ctx.channel.id
        query = {"_id": channel}
        results = collection.find_one(query)

        if results is not None:
            battlemap = results['battlemap']
        else:
            await ctx.send("This channel has no assigned battlemap.")
            return

        author = battlemap['author']

        if len(battlemap['editors']) == 0:
            editor_list = (f"Author: <@{author}>\n\nEditors: This battlemap "
                           "has no editors. Add a new editor with the "
                           "addeditor command.")
        else:
            editor_list = f"Author: <@{author}>\n\nEditors:"

        for i in battlemap['editors']:
            editor_list += f"\n -<@{i}>"

        embed = discord.Embed(title="Editor list:", description=editor_list)

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Battlemap(client))
