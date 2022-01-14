import discord


# Skills are split in half for side-by-side display.
skills_1 = ["anthropology", "accounting", "appraise", "archaeology", "charm",
            "climb", "credit_rating", "cthulhu_mythos", "disguise", "dodge",
            "drive_automobile", "electrical_repair", "fast_talk",
            "fighting_brawl", "firearms_handgun", "firearms_rifle_shotgun",
            "first_aid", "history", "spot_hidden", "swim", "track",
            "additional_skill_2", "additional_skill_4"]
skills_2 = ["intimidate", "jump", "language_own", "law", "library_use",
            "listen", "locksmith", "mechanical_repair", "medicine",
            "natural_world", "navigate", "occult", "operate_heavy_machine",
            "persuade", "psychoanalysis", "psychology", "ride",
            "sleight_of_hand", "stealth", "throw", "additional_skill_1",
            "additional_skill_3", "additional_skill_5"]
stats = ["strength", "dexterity", "power", "constitution", "appearance",
         "education", "size", "intelligence"]
other_stats = ["hp", "mp", "luck", "sanity", "move_rate", "damage_bonus",
               "build", "dodge"]

ascii_cthulhu = """    @@   @@@@@@@@   @@
   @@@  @@@@@@&&&&  @@@
  @@@@  &&&&&&&&&@  @@@@
 @@@@@@@&&&&&&&&@@@@@@@@@
 @@@@@@@@@&&&&&@@@@@@@@@@
 @@@@   @&&&&&&&&&   @@@@
 @@    @& &&  @@ @@    @@
 @    @ @ @@  @@ @ @    @
"""


class CallOfCthulhu_Character:
    def __init__(self, name):
        self.system = "Call of Cthulhu 7e"
        self.image = ("https://publicdomainvectors.org/photos/abstract-user-"
                      "flat-1.png")

        # Investigator Info
        self.name = name
        self.occupation = ""
        self.age = ""
        self.sex = ""
        self.residence = ""
        self.birthplace = ""

        # Characteristics
        self.strength = 0
        self.constitution = 0
        self.size = 0
        self.dexterity = 0
        self.appearance = 0
        self.intelligence = 0
        self.power = 0
        self.education = 0
        self.move_rate = 0

        self.hp = 0
        self.maximum_hp = 0
        self.luck = 0
        self.mp = 0
        self.maximum_mp = 0
        self.damage_bonus = 0
        self.build = 0
        self.dodge = 0

        self.damage_bonus = 0
        self.build = 0

        self.sanity = 0
        self.maximum_sanity = 0
        self.temporary_insanity = False
        self.indefinite_insanity = False
        self.major_wound = False
        self.unconscious = False
        self.dying = False

        # Investigator Skills
        self.accounting_proficiency = False
        self.accounting = 0
        self.anthropology_proficiency = False
        self.anthropology = 0
        self.appraise_proficiency = False
        self.appraise = 0
        self.archaeology_proficiency = False
        self.archaeology = 0
        self.charm_proficiency = False
        self.charm = 0
        self.climb_proficiency = False
        self.climb = 0
        self.credit_rating_proficiency = False
        self.credit_rating = 0
        self.cthulhu_mythos_proficiency = False
        self.cthulhu_mythos = 0
        self.disguise_proficiency = False
        self.disguise = 0
        self.dodge_proficiency = False
        self.dodge = 0
        self.drive_automobile_proficiency = False
        self.drive_automobile = 0
        self.electrical_repair_proficiency = False
        self.electrical_repair = 0
        self.fast_talk_proficiency = False
        self.fast_talk = 0
        self.fighting_brawl_proficiency = False
        self.fighting_brawl = 0
        self.firearms_handgun_proficiency = False
        self.firearms_handgun = 0
        self.firearms_rifle_shotgun_proficiency = False
        self.firearms_rifle_shotgun = 0
        self.first_aid_proficiency = False
        self.first_aid = 0
        self.history_proficiency = False
        self.history = 0

        self.intimidate_proficiency = False
        self.intimidate = 0
        self.jump_proficiency = False
        self.jump = 0
        self.language_own_proficiency = False
        self.language_own = 0
        self.law_proficiency = False
        self.law = 0
        self.library_use_proficiency = False
        self.library_use = 0
        self.listen_proficiency = False
        self.listen = 0
        self.locksmith_proficiency = False
        self.locksmith = 0
        self.mechanical_repair_proficiency = False
        self.mechanical_repair = 0
        self.medicine_proficiency = False
        self.medicine = 0
        self.natural_world_proficiency = False
        self.natural_world = 0
        self.navigate_proficiency = False
        self.navigate = 0
        self.occult_proficiency = False
        self.occult = 0
        self.operate_heavy_machine_proficiency = False
        self.operate_heavy_machine = 0
        self.persuade_proficiency = False
        self.persuade = 0
        self.psychoanalysis_proficiency = False
        self.psychoanalysis = 0
        self.psychology_proficiency = False
        self.psychology = 0
        self.ride_proficiency = False
        self.ride = 0
        self.sleight_of_hand_proficiency = False
        self.sleight_of_hand = 0

        self.spot_hidden_proficiency = False
        self.spot_hidden = 0
        self.stealth_proficiency = False
        self.stealth = 0
        self.swim_proficiency = False
        self.swim = 0
        self.throw_proficiency = False
        self.throw = 0
        self.track_proficiency = False
        self.track = 0
        self.additional_skill_1_proficiency = False
        self.additional_skill_1_name = ""
        self.additional_skill_1 = 0
        self.additional_skill_2_proficiency = False
        self.additional_skill_2_name = ""
        self.additional_skill_2 = 0
        self.additional_skill_3_proficiency = False
        self.additional_skill_3_name = ""
        self.additional_skill_3 = 0
        self.additional_skill_4_proficiency = False
        self.additional_skill_4_name = ""
        self.additional_skill_4 = 0
        self.additional_skill_5_proficiency = False
        self.additional_skill_5_name = ""
        self.additional_skill_5 = 0

        # Inventory
        self.inventory = ""
        self.currency = 0
        self.assets = ""

        # Backstory
        self.description = ""
        self.ideology_and_beliefs = ""
        self.significant_people = ""
        self.meaningful_locations = ""
        self.treasured_possessions = ""
        self.traits = ""
        self.injuries_and_scars = ""
        self.phobias_and_manias = ""
        self.arcane_tomes_and_spells = ""
        self.encounters_with_strange_entities = ""

    def make_page_1(char, player):
        def x(a): return "🗹" if a else "☐"

        def y(a): return char[f"{a}_name"] if char[f"{a}_name"] else \
            "Additional Skill"

        desc = f"**Player:** {player}```css\n"
        skills_field_1 = "```css\n"

        for a, b, c in zip(stats, other_stats,
                           iter(ascii_cthulhu.splitlines())):
            if b == "hp" or b == "mp":
                line = f"{b.upper()}: {char[b]}/{char[f'maximum_{b}']}\n"
            elif b == "dodge":
                line = f"Dodge: {char[b]}|{int(char[b]/2)}|{int(char[b]/5)}\n"
            else:
                line = f"{b.title().replace('_', ' ')}: {char[b]}\n"

            desc = desc + (f"{a[:3].upper()}: {int(char[a]):02d}|"
                           f"{int(char[a]/2):02d}|{int(char[a]/5):02d}"
                           .ljust(15) + f"{c}").ljust(42) +\
                line

        for a, b in zip(skills_1, skills_2):
            ax = a.replace('_', ' ').title()
            bx = b.replace('_', ' ').title()

            if a == "fighting_brawl":
                ax = "Fighting (Brawl)"
            if a == "firearms_handgun":
                ax = "Firearms (H)"
            if a == "firearms_rifle_shotgun":
                ax = "Firearms (R/S)"
            if a == "electrical_repair":
                ax = "Elec. Repair"
            if b == "operate_heavy_machine":
                bx = "Op. Hv. Machine"
            if b == "mechanical_repair":
                bx = "Mch. Repair"
            if "additional_skill" in a:
                ax = y(a)
            if "additional_skill" in b:
                bx = y(b)

            line = (f"{x(char[f'{a}_proficiency'])} {ax}:".ljust(20) +
                    f"{char[a]:02d}|{int(char[a]/2):02d}|"
                    f"{int(char[a]/5):02d}".rjust(9))
            line = line.ljust(30) + (f"{x(char[f'{b}_proficiency'])} "
                                     f"{bx}:".ljust(20) +
                                     f"{char[b]:02d}|{int(char[b]/2):02d}|"
                                     f"{int(char[b]/5):02d}\n".rjust(10))
            skills_field_1 = skills_field_1 + line

        skills_field_1 = skills_field_1 + "```"
        desc = desc + "```" + skills_field_1
        # "invisible characters" are needed for additional spacing on fields
        # that don't contain code blocks.
        sanity_field = (f"{x(char['temporary_insanity'])} "
                        f"Temporary Insanity ᲼᲼ "
                        f"{x(char['indefinite_insanity'])} "
                        f"Indefinite Insanity ᲼᲼"
                        f" {x(char['major_wound'])} Major Wound\n"
                        f"{x(char['unconscious'])} Unconscious᲼᲼᲼᲼᲼᲼᲼᲼"
                        f"{x(char['dying'])} Dying")

        page_1 = discord.Embed(description=desc)
        page_1.add_field(name="Ailments:", value=sanity_field, inline=False)
        page_1.set_footer(text="Page 1/2")

        if char['image']:
            page_1.set_author(name=f"{char['system']}: {char['name']}",
                              icon_url=char['image'])
        else:
            page_1.set_author(name=f"{char['system']}: {char['name']}")

        return page_1

    def make_page_2(char, player):
        def x(a): return char[a] if char[a] else None

        description = f"**Description:**\n{char['description']}"
        page_2 = discord.Embed(description=description)

        for i in ("ideology_and_beliefs", "significant_people",
                  "meaningful_locations", "treasured_possessions", "traits",
                  "injuries_and_scars", "phobias_and_manias",
                  "arcane_tomes_and_spells",
                  "encounters_with_strange_entities"):
            page_2.add_field(name=i.replace("_", " ").title() + ":",
                             value=x(i))

        page_2.set_footer(text="Page 2/2")

        if char['image']:
            page_2.set_author(name=f"{char['system']} {char['name']}",
                              icon_url=char['image'])
        else:
            page_2.set_author(name=f"{char['system']} {char['name']}")

        return page_2
