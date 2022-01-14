import discord as d
import aiohttp
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from modules.embeds import *


class srd_search(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.file = None

    @cog_ext.cog_slash(name="dndsearch",
                       description="Search for 'search_item' in the "
                                   "'search_category' of the Dungeons & "
                                   "Dragons 5th Edition SRD.",
                       options=[
                        create_option(
                            name="search_category",
                            description="Category to be searched. Execute "
                                        "without a search item to query all "
                                        "items in the selected category.",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(name="Ability Scores",
                                              value="ability-scores"),
                                create_choice(name="Skills",
                                              value="skills"),
                                create_choice(name="Proficiencies",
                                              value="proficiencies"),
                                create_choice(name="Languages",
                                              value="languages"),
                                create_choice(name="Alignments",
                                              value="alignments"),
                                create_choice(name="Backgrounds",
                                              value="backgrounds"),
                                create_choice(name="Classes",
                                              value="classes"),
                                create_choice(name="Subclasses",
                                              value="subclasses"),
                                create_choice(name="Features",
                                              value="features"),
                                create_choice(name="Races",
                                              value="races"),
                                create_choice(name="Subraces",
                                              value="subraces"),
                                create_choice(name="Traits",
                                              value="traits"),
                                create_choice(name="Equipment Categories",
                                              value="equipment-categories"),
                                create_choice(name="Equipment",
                                              value="equipment"),
                                create_choice(name="Magic Items",
                                              value="magic-items"),
                                create_choice(name="Spells",
                                              value="spells"),
                                create_choice(name="Feats",
                                              value="feats"),
                                create_choice(name="Monsters",
                                              value="monsters"),
                                create_choice(name="Conditions",
                                              value="conditions"),
                                create_choice(name="Damage Types",
                                              value="damage-types"),
                                create_choice(name="Magic Schools",
                                              value="magic-schools"),
                                create_choice(name="Rules",
                                              value="rules"),
                                create_choice(name="Rule Sections",
                                              value="rule-sections"),
                            ]),
                        create_option(
                            name="search_item",
                            description="Item to be searched.",
                            option_type=3,
                            required=False
                        ),
                        create_option(
                            name="search_param",
                            description="Additional search parameter "
                                        "(optional).",
                            option_type=3,
                            required=False
                        ),
                        create_option(
                            name="search_param2",
                            description="Second additional search parameter "
                                        "(optional).",
                            option_type=3,
                            required=False
                        ),
                        create_option(
                            name="search_param3",
                            description="Third additional search parameter "
                                        "(optional).",
                            option_type=3,
                            required=False
                        )])
    async def search(self, ctx, search_category, search_item="",
                     search_param="", search_param2="",
                     search_param3=""):
        """Requests search_item on search_category with search_params from the
        D&D 5e API and sends the results to the appropriate function for embed
        generation. The returning embed is returned to the user."""
        search_category = search_category.replace("_", "-").replace(" ", "-")
        search_item = search_item.replace("_", "-").replace(" ", "-")
        search_param = search_param.replace("_", "-").replace(" ", "-")
        search_param2 = search_param2.replace("_", "-").replace(" ", "-")
        search_param3 = search_param3.replace("_", "-").replace(" ", "-")

        if search_param2 and not search_param3:
            async with aiohttp.ClientSession() as session:
                url = (f"http://www.dnd5eapi.co/api/{search_category}/"
                       f"{search_item}/{search_param}/{search_param2}")

                async with session.get(url) as info:
                    info = await info.json()

        elif search_param3:
            async with aiohttp.ClientSession() as session:
                url = (f"http://www.dnd5eapi.co/api/{search_category}/"
                       f"{search_item}/{search_param}/{search_param2}/"
                       f"{search_param3}")

                async with session.get(url) as info:
                    info = await info.json()

        else:
            async with aiohttp.ClientSession() as session:
                url = (f"http://www.dnd5eapi.co/api/{search_category}/"
                       f"{search_item}/{search_param}")

                async with session.get(url) as info:
                    info = await info.json()

        if not search_item:
            # If there is a search category and no search item, the search
            # category's items are partially displayed.
            results = info['results']
            cursor = 0
            search_category = search_category.replace("-", " ").title()

            def make_page(cursor):
                display = "**Results:**"
                cursor_10 = cursor + 10

                for i in range(cursor, cursor_10):
                    try:
                        display += "\n" + results[i]['name']
                    except Exception:
                        pass

                page = d.Embed(title=f"Search Results: {search_category}",
                                     description=(f"**Matches:** "
                                                  f"{info['count']}"
                                                  f"\n{display}"))

                return page, display

            def check(reaction, user):
                return user == ctx.author

            # for i in info['results']:
            #     results += f"{info['results'][cursor]['index']}\n"
            #     cursor += 1

            # results = u.adjust_length(results, 1000)
            page, display = make_page(cursor)

            page.set_footer(text="Open Game License v 1.0a Copyright 2000, "
                                 "Wizards of the Coast, LLC.")

            message = await ctx.send(embed=page)
            message_id = message.id
            reaction = None
            user = None

            await message.add_reaction('◀')
            await message.add_reaction('▶')

            while True:
                if reaction is not None and reaction.message.id == message_id:
                    if str(reaction) == '◀':
                        # Previous page in character sheet.
                        cursor -= 10
                        if cursor >= 0:
                            results[cursor]
                            page, display = make_page(cursor)

                            page.set_footer(text="Open Game License v 1.0a "
                                                 "Copyright 2000, Wizards of"
                                                 " the Coast, LLC.")

                            if len(display) > 13:
                                await message.edit(embed=page)
                        else:
                            cursor = 0
                            pass

                        if len(display) > 13:
                            await message.edit(embed=page)

                    elif str(reaction) == '▶':
                        # Next page in character sheet.
                        cursor += 10
                        try:
                            results[cursor]
                            page, display = make_page(cursor)

                            page.set_footer(text="Open Game License v 1.0a "
                                                 "Copyright 2000, Wizards of"
                                                 " the Coast, LLC.")

                            if len(display) > 13:
                                await message.edit(embed=page)
                        except Exception:
                            cursor -= 10
                            pass

                        if len(display) > 13:
                            await message.edit(embed=page)

                try:
                    reaction, user = await self.client.wait_for('reaction_add',
                                                                timeout=60.0,
                                                                check=check)
                    await message.remove_reaction(reaction, user)
                except Exception:
                    break

            await message.clear_reactions()

        else:
            # search_category and search_item are combined and used as the name
            # of the function that will create the returning embed.
            if search_param and not search_param2 and not search_param3:
                search_category += f"_{search_param}"
                search_function = globals()[search_category.replace("-", "_")]
                embed, self.file = search_function(ctx, search_item, info)

            elif search_param and search_param2 and not search_param3:
                if search_param2.isnumeric():
                    search_category += f"_{search_param}_"
                    search_function = globals()[search_category.replace("-",
                                                                        "_")]
                    embed, self.file = search_function(ctx, search_item, info,
                                                       search_param2)

                else:
                    search_category += f"_{search_param}_{search_param2}"
                    search_function = globals()[search_category.replace("-",
                                                                        "_")]
                    embed, self.file = search_function(ctx, search_item, info,
                                                       search_param2)

            elif search_param3:
                search_category += f"_{search_param}_{search_param3}"
                search_function = globals()[search_category.replace("-", "_")]
                embed, self.file = search_function(ctx, search_item, info,
                                                   search_param2)

            else:
                search_function = globals()[search_category.replace("-", "_")]
                embed, self.file = search_function(ctx, search_item, info)

            embed.set_footer(text="Open Game License v 1.0a Copyright 2000, "
                                  "Wizards of the Coast, LLC.")

            if self.file:
                await ctx.send(file=self.file, embed=embed)
                self.file = ""
            else:
                await ctx.send(embed=embed)


def setup(client):
    client.add_cog(srd_search(client))
