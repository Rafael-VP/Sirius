import discord


class FateCore_Character:
    """Holds attribute values for a Fate Core character sheet.
    New instances are passed through the character encoder and
    becomee json serializable for database storage."""

    def __init__(self, name):
        self.system = "Fate Core"
        self.image = ("https://publicdomainvectors.org/photos/abstract-user-"
                      "flat-1.png")
        self.name = name
        self.description = "None"
        self.refresh = 0

        self.high_concept = "None"
        self.trouble = "None"
        self.aspects = "None"

        self.superb_skills = "None"
        self.great_skills = "None"
        self.good_skills = "None"
        self.fair_skills = "None"
        self.average_skills = "None"

        self.extras = "None"
        self.stunts = "None"

        self.level_1_physical_stress = False
        self.level_2_physical_stress = False
        self.level_3_physical_stress = False
        self.level_4_physical_stress = False
        self.level_1_mental_stress = False
        self.level_2_mental_stress = False
        self.level_3_mental_stress = False
        self.level_4_mental_stress = False

        self.mild_consequences = "None"
        self.second_mild_consequences = "None"
        self.moderate_consequences = "None"
        self.severe_consequences = "None"

        self.inventory = ""
        self.currency = 0

    def make_page_1(char, player):
        stresses = ["level_1_physical_stress", "level_2_physical_stress",
                    "level_3_physical_stress", "level_4_physical_stress",
                    "level_1_mental_stress", "level_2_mental_stress",
                    "level_3_mental_stress", "level_4_mental_stress"]
        physical_stress = "Physical (Physique):\n"
        mental_stress = "Mental (Will):\n"
        physical_counter = 1
        mental_counter = 1

        def x(a): return "🗹" if a else "☐"

        for i in stresses:
            if "physical" in i:
                physical_stress += f"{physical_counter} {x(char[i])} "
                physical_counter += 1
            else:
                mental_stress += f"{mental_counter} {x(char[i])} "
                mental_counter += 1

        aspects_field = (f"High Concept: {char['high_concept']}\n"
                         f"Trouble: {char['trouble']}\n"
                         f"Aspects: {char['aspects']}")
        skills_field = (f"Superb (+5): {char['superb_skills']}\n"
                        f"Great (+4): {char['great_skills']}\n"
                        f"Good (+3): {char['good_skills']}\n"
                        f"Fair (+2): {char['fair_skills']}\n"
                        f"Average (+1): {char['average_skills']}")
        stress_field = f"{physical_stress}\n{mental_stress}"
        consequences_field = (f"2 Mild: {char['mild_consequences']}\n 4 "
                              f"Moderate: {char['moderate_consequences']}\n"
                              f"6 Severe: {char['moderate_consequences']}\n"
                              f"2 Mild: {char['mild_consequences']}\n")

        page1 = discord.Embed(description=f"**Player:** {player}\n**Character "
                                          f"Name:** {char['name']}\n**Refresh:"
                                          f"** {char['refresh']}\n**Descriptio"
                                          f"n:**\n{char['description']}")
        page1.add_field(name="ASPECTS", value=aspects_field)
        page1.add_field(name="SKILLS", value=skills_field)
        page1.add_field(name="EXTRAS", value=f"{char['extras']}\u200b",
                        inline=True)
        page1.add_field(name="STUNTS", value=f"{char['stunts']}\u200b",
                        inline=True)
        page1.add_field(name="STRESS", value=stress_field)
        page1.add_field(name="CONSEQUENCES", value=consequences_field)

        if char['image']:
            page1.set_author(name=f"{char['system']}: {char['name']}")
            page1.set_thumbnail(url=char['image'])
        else:
            page1.set_author(name=f"{char['system']}: {char['name']}")

        return page1
