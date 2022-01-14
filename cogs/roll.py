import discord as d
from discord.ext import commands
from discord_slash import cog_ext
import rolldice
import random
import modules.utility as u


class Roll(commands.Cog):
    """Handles regular dice and fudge dice rolls."""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.client}.")

    def has_numbers(self, inputString):
        """Check if a string contains any numbers."""
        return any(char.isdigit() for char in inputString)

    def repeat_roll(self, amount, die):
        """Repeats any given roll {amount} times and returns the result with
        each roll separated by a newline character."""
        r = ""
        e = ""
        for i in range(0, amount):
            result, explanation = rolldice.roll_dice(die)
            r += f", {str(result)}"
            e += f", {str(explanation)}"

        return r[2:], e[2:]

    def check_roll(self, string):
        """Checks if a string is a valid dice roll or mathematical
        operation."""
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

    @commands.Cog.listener()
    async def on_message(self, message):
        """Parses and executes dice rolls without prefix. Exceptions are
        handled passively."""
        ctx = await self.client.get_context(message)
        content = message.content

        if ctx.valid:
            return
        if message.author == self.client.user:
            return
        if len(content.replace(' ', '')) > 10:
            return
        if "d1!" in content:
            return
        if not self.check_roll(content):
            return

        if any(map(str.isdigit, content)):
            if '#' in content and 'd' in content:
                partitioned_dice = content.partition('#')
                die = partitioned_dice[2]
                amount = int(partitioned_dice[0])

                if amount > 100 or int(die[-1]) > 99:
                    return

                try:
                    result, explanation = self.repeat_roll(amount, die)
                except Exception:
                    return

            else:
                try:
                    result, explanation = rolldice.roll_dice(content)
                except Exception:
                    return

            explanation = explanation.replace("**", "^")
            explanation = u.adjust_length(explanation.replace("*", "\\*"),
                                          4000)
            disp = str(F"""```css\n{result}```""")

            if len(explanation) > 256:
                embed = d.Embed(title=f":game_die: {content}",
                                description=f"{explanation}\n{disp}")
            else:
                embed = d.Embed(title=f":game_die: {content}")
                embed.add_field(name=explanation, value=disp)

            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="roll",
                       description="Rolls dice and performs mathematical "
                                   "operations.")
    async def roll(self, ctx, *, dice):
        """Parses a message and executes any rolls within it."""

        if "d1!" in dice:  # have this in the beggining instead
            await ctx.send("Invalid dice roll.")
            return
        elif len(dice.replace(' ', '')) > 10:
            await ctx.send("Oversized dice roll.")
            return

        if '#' in dice and self.has_numbers(dice):
            partitioned_dice = dice.partition('#')
            die = partitioned_dice[2]
            amount = int(partitioned_dice[0])

            if amount > 100:
                await ctx.send("Oversized dice roll.")
                return
            else:
                try:
                    result, explanation = self.repeat_roll(amount, die)
                except Exception:
                    await ctx.send("Invalid dice roll.")
                    return
        else:
            try:
                result, explanation = rolldice.roll_dice(dice)
            except Exception:
                await ctx.send("Invalid dice roll.")
                return

        explanation = explanation.replace("**", "^")
        explanation = u.adjust_length(explanation.replace("*", "\\*"), 4000)
        disp = str(F"""```css\n{result}```""")

        if len(explanation) > 256:
            embed = d.Embed(title=f":game_die: {dice}",
                            description=f"**{explanation}**\n{disp}")
        else:
            embed = d.Embed(title=f":game_die: {dice}")
            embed.add_field(name=explanation, value=disp)

        await ctx.send(embed=embed)
        return

    @cog_ext.cog_slash(name="fudge",
                       description="Rolls fudge/fate dice.",
                       options=[
                        {
                            "name": "dice_count",
                            "description": ("Amount of fudge dice to be rolled"
                                            ", up to 8 at a time."),
                            "type": 4,
                            "required": "False"
                        }])
    async def fudge(self, ctx, dice_count=4):
        """Parses and rolls fudge dice. A face is chosen pseudorandomly for
        every rolled die and the result is returned through an embed with
        emotes representing the faces and a numerical sum of all rolled
        dice."""
        explanation = []
        emotes = ""
        result = 0
        dice_count = int(dice_count)

        try:
            if not dice_count > 0 or not dice_count <= 8:
                await ctx.send("Invalid dice count.")
                return

            for number in range(0, dice_count):
                # The explanation is a literal version of the operation, while
                # result is the numeric sum of all rolled dice.
                face = random.choice([-1, 0, +1])
                explanation.append(face)
                result += face

            for i in explanation:
                # Emotes are used to represent each die from the explanation,
                # simulating fudge die faces.
                if i == -1:
                    emotes = emotes + " <:blue_minus:873570599656624138>"
                elif i == 0:
                    emotes = emotes + " <:blank:873570614357655592>"
                else:
                    emotes = emotes + " <:blue_plus:873570582699053077>"

            disp = str(f"""```css\n{result}```""")
            embed = d.Embed(title=f":game_die: {str(dice_count)}dF")
            embed.add_field(name=f"{emotes}", value=disp)
            await ctx.send(embed=embed)
            return

        except Exception:
            await ctx.send("Invalid expression.")
            return

    @cog_ext.cog_slash(name="coinflip", description="Flips a coin.")
    async def coinflip(self, ctx):
        """Performs a pseudorandom choice between heads and tails and returns
        the result through the corresponding GIF in an embed."""

        result = random.choice(['heads', 'tails'])
        coin_file = d.File(f"data/coinflip/{result}.gif")
        embed = d.Embed(title=f"{result.title()}!")
        embed.set_image(url=f"attachment://{result}.gif")

        await ctx.send(embed=embed, file=coin_file)
        return


def setup(client):
    client.add_cog(Roll(client))
