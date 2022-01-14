import discord
from discord.ext import commands
from discord_slash import cog_ext
import rolldice as rd


rollers = []


class Roller(commands.Cog):
    """Handles roller generation and interactions. Rollers are embeds created
    to temporarily hold and perform self-contained dice rolls. User input is
    prompted with reaction emotes and roller information is updated through
    message edits."""
    def __init__(self, client):
        self.client = client

    def make_page(self, ctx, die, result=' ', log='-', amount=1, modifier='0'):
        """Creates embeds for roller instances."""
        page = discord.Embed(title=f"🎲 {str(ctx.author)[:-5]}'s Roller",
                             description=f"""Rolling {amount}{die} + {modifier}\
                             ```css\n{result}```""")
        page.add_field(name="Log", value=f"{log}", inline=True),

        return page

    @cog_ext.cog_slash(name="roller",
                       description="Creates a roller in this channel.")
    async def roller(self, ctx):
        """Generates a roller instance and handles roller interactions."""
        author = ctx.author.id
        dice = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100']
        result_display = "---"

        if author in rollers:
            await ctx.send("You may only have one active roller at a time.")
            return

        rollers.append(author)
        page = self.make_page(ctx, dice[0], result_display)

        message = await ctx.send(embed=page)
        await message.add_reaction('⬇️')
        await message.add_reaction('⬆️')
        await message.add_reaction('◀')
        await message.add_reaction('🎲')
        await message.add_reaction('▶')
        await message.add_reaction('<:blue_minus:873570599656624138>')
        await message.add_reaction('<:blue_plus:873570582699053077>')

        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None
        user = None
        log = []
        amount = 1
        modifier = 0

        while True:
            if str(reaction) == '◀':  # Previous die type in dice dict
                if i > 0:
                    i -= 1
                    amount = amount
                    new_page = self.make_page(ctx, dice[i],
                                              result=result_display, log=log,
                                              amount=amount, modifier=modifier)
                    await message.edit(embed=new_page)

                else:
                    i = 6
                    amount = amount
                    new_page = self.make_page(ctx, dice[i],
                                              result=result_display, log=log,
                                              amount=amount, modifier=modifier)
                    await message.edit(embed=new_page)

            elif str(reaction) == '▶':  # Next die type in dice dict.
                if i < 6:
                    i += 1
                    amount = amount
                    new_page = self.make_page(ctx, dice[i],
                                              result=result_display, log=log,
                                              amount=amount, modifier=modifier)
                    await message.edit(embed=new_page)

                else:
                    i = 0  # Goes back to beginning if already at the last die.
                    amount = amount
                    new_page = self.make_page(ctx, dice[i],
                                              result=result_display, log=log,
                                              amount=amount, modifier=modifier)
                    await message.edit(embed=new_page)

            elif str(reaction) == '🎲':  # Rolls current dice configuration.
                try:
                    result, explanation = rd.roll_dice(str(amount) + dice[i]
                                                       + "+" + str(modifier))
                except Exception:
                    result = "---"  # Answer to invalid rolls.

                log.insert(0, result)  # Adds a new roll to log and removes
                if len(log) > 16:      # the oldest roll above the limit.
                    log.pop(-1)
                amount = amount
                result_display = f"{explanation} = {result}"

                new_page = self.make_page(ctx, dice[i], result=result_display,
                                          log=log, amount=amount,
                                          modifier=modifier)
                await message.edit(embed=new_page)

            elif str(reaction) == '⬇️':
                # Decreases dice count (cannot be negative).
                if amount == 1:
                    pass
                else:
                    amount -= 1
                    new_page = self.make_page(ctx, dice[i],
                                              result=result_display,
                                              log=log, amount=amount,
                                              modifier=modifier)
                    await message.edit(embed=new_page)

            elif str(reaction) == '⬆️':
                # Increases dice count.
                amount += 1
                new_page = self.make_page(ctx, dice[i], result=result_display,
                                          log=log, amount=amount,
                                          modifier=modifier)
                await message.edit(embed=new_page)

            elif str(reaction) == '<:blue_minus:873570599656624138>':
                # Decreases modifier (can be negative).
                modifier -= 1
                new_page = self.make_page(ctx, dice[i], result=result_display,
                                          log=log, amount=amount,
                                          modifier=modifier)
                await message.edit(embed=new_page)

            elif str(reaction) == '<:blue_plus:873570582699053077>':
                # Increases modifier.
                modifier += 1
                new_page = self.make_page(ctx, dice[i], result=result_display,
                                          log=log, amount=amount,
                                          modifier=modifier)
                await message.edit(embed=new_page)

            try:
                # Rollers are deactivated if inactive for more than 10 minutes
                reaction, user = await self.client.wait_for('reaction_add',
                                                            timeout=1800.0,
                                                            check=check)
                await message.remove_reaction(reaction, user)
            except Exception:
                break

        await message.clear_reactions()

        rollers.remove(author)
        return


def setup(client):
    client.add_cog(Roller(client))
