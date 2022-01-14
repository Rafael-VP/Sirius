import modules.dnd as dd
import modules.utility as u
import discord


skills = ["acrobatics", "arcana", "athletics", "crafting", "deception",
          "diplomacy", "intimidation", "medicine", "nature", "occultism",
          "performance", "religion", "society", "stealth", "survival",
          "thievery", "lore_skill_1", "lore_skill_2"]
stats_skills = {
    "STR": ["athletics"],
    "DEX": ["acrobatics", "thievery", "stealth"],
    "INT": ["arcana", "occultism", "society", "religion",
            "crafting"],
    "WIS": ["insight", "medicine", "survival", "nature"],
    "CHA": ["deception", "intimidation", "performance", "diplomacy"]
}


class Pathfinder2e_Character:
    def __init__(self, name, cclass="", level=0):
        self.system = "Pathfinder 2e"
        self.image = ("https://publicdomainvectors.org/photos/abstract-user-"
                      "flat-1.png")
        self.name = name
        self.cclass = cclass
        self.level = level
        self.experience = 0
        self.description = ""
        self.race = ""
        self.ancestry_and_heritage = None
        self.background = None
        self.size = None
        self.alignment = None
        self.traits = None
        self.deity = None
        self.hero_points = 0

        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.charisma = 10

        self.class_dc = 10
        self.movement = "30 ft."

        self.armor_class = 10
        self.hit_points = 0
        self.maximum_hit_points = 0
        self.temporary_hit_points = 0
        self.resistances_and_immunities = ""
        self.conditions = ""

        self.fortitude = 0
        self.reflex = 0
        self.will = 0

        self.perception = 0
        self.senses = ""

        self.acrobatics = 0
        self.arcana = 0
        self.athletics = 0
        self.crafting = 0
        self.deception = 0
        self.diplomacy = 0
        self.intimidation = 0
        self.lore_skill_1 = 0
        self.lore_skill_1_name = ""
        self.lore_skill_2 = 0
        self.lore_skill_2_name = ""
        self.medicine = 0
        self.nature = 0
        self.occultism = 0
        self.performance = 0
        self.religion = 0
        self.society = 0
        self.stealth = 0
        self.survival = 0
        self.thievery = 0
        self.lore_skill_1_name = ""
        self.lore_skill_1 = 0
        self.lore_skill_2_name = ""
        self.lore_skill_2 = 0

        self.languages = ""

        self.ancestry_feats_and_abilities = ""
        self.skill_feats = ""
        self.general_feats = ""
        self.class_feats_and_abilities = ""
        self.bonus_feats = ""

        self.ethnicity = None
        self.nationality = None
        self.birthplace = None
        self.age = None
        self.height = None
        self.weight = None

        self.inventory = ""
        self.currency = 0

        self.spell_attack_roll = 0
        self.spell_dc = 0

        self.cantrips = ""
        self.level_1_spells = ""
        self.level_1_spell_slots = 0
        self.maximum_level_1_spell_slots = 0
        self.level_2_spells = ""
        self.level_2_spell_slots = 0
        self.maximum_level_2_spell_slots = 0
        self.level_3_spells = ""
        self.level_3_spell_slots = 0
        self.maximum_level_3_spell_slots = 0
        self.level_4_spells = ""
        self.level_4_spell_slots = 0
        self.maximum_level_4_spell_slots = 0
        self.level_5_spells = ""
        self.level_5_spell_slots = 0
        self.maximum_level_5_spell_slots = 0
        self.level_6_spells = ""
        self.level_6_spell_slots = 0
        self.maximum_level_6_spell_slots = 0
        self.level_7_spells = ""
        self.level_7_spell_slots = 0
        self.maximum_level_7_spell_slots = 0
        self.level_8_spells = ""
        self.level_8_spell_slots = 0
        self.maximum_level_8_spell_slots = 0
        self.level_9_spells = ""
        self.level_9_spell_slots = 0
        self.maximum_level_9_spell_slots = 0
        self.level_10_spells = ""
        self.level_10_spell_slots = 0
        self.maximum_level_10_spell_slots = 0

    def make_page_1(char, player):
        def y(a): return a if a else "None"
        def z(a): return f"+{a}" if int(a) > 0 else a

        page_1 = discord.Embed(description=f"**Player:** {player}")
        saving_throws = (f"Fortitude: {char['fortitude']}\n"
                         f"Reflex: {char['reflex']}\nWill: {char['will']}")
        skills_field = "```css\n"
        cursor = 1
        stats = "```css\n"
        stats_label = ""

        for i in skills:
            skill = "WIS"

            for key, value in stats_skills.items():
                for s in value:
                    if s == i:
                        skill = key

            if "lore_skill_" in i:
                a = "" + char[f"{i}_name"]+" Lore" if char[f"{i}_name"] \
                    else "___ Lore"
            else:
                a = i.title()

            skills_field += (f"{a} ({skill}):".ljust(24) +
                             f"{z(char[i])}\n".rjust(5))

        skills_field = skills_field + "```"

        for i in ["strength", "dexterity", "constitution", "intelligence",
                  "wisdom", "charisma"]:
            stat = dd.get_modifier(char[i])
            stats_label = stats_label.ljust(12*cursor) + f"{i[:3].upper()}"

            stats = stats.ljust(10*cursor) + f"{char[i]}({stat})"
            cursor += 1

        stats = stats + "```".ljust(80)
        stats_label = "```" + stats_label[7:].ljust(74) + "```"

        page_1.add_field(name="Class:", value=char['cclass'].title())
        page_1.add_field(name="Level:",
                         value=f"{char['level']} ({char['experience']} exp.)")
        page_1.add_field(name="Hero Points:", value=char['hero_points'])
        page_1.add_field(name=stats_label, value=stats, inline=False)
        page_1.add_field(name="Armor Class:", value=char['armor_class'])
        page_1.add_field(name="Hit Points:",
                         value=f"{char['hit_points']} / "
                               f"{char['maximum_hit_points']}")
        page_1.add_field(name='Temporary Hit Points:',
                         value=char['temporary_hit_points'])
        page_1.add_field(name="Class DC:", value=char['class_dc'])
        page_1.add_field(name="Saving Throws:", value=saving_throws)
        page_1.add_field(name="Perception:",
                         value=f"[{char['perception']}]\nSenses: "
                               f"{char['senses']}")
        page_1.add_field(name="Skills:", value=skills_field)
        page_1.add_field(name="Ancestry Feats and Abilities:",
                         value=y(char['ancestry_feats_and_abilities']))
        page_1.add_field(name="Class Feats and Abilities:",
                         value=y(char['class_feats_and_abilities']),
                         inline=False)
        page_1.add_field(name="Skill Feats:", value=y(char['skill_feats']))
        page_1.add_field(name="General Feats:", value=y(char['general_feats']))
        page_1.add_field(name="Bonus Feats:", value=y(char['bonus_feats']))
        page_1.add_field(name='Movement:', value=y(char['movement']))
        page_1.add_field(name='Resistances and Immunities:',
                         value=y(char['resistances_and_immunities']))
        page_1.add_field(name='Conditions:', value=y(char['conditions']))
        page_1.set_footer(text="Page 1/3")

        if char['image']:
            page_1.set_author(name=f"{char['system']}: {char['name']}",
                              icon_url=char['image'])
        else:
            page_1.set_author(name=f"{char['system']}: {char['name']}")

        return page_1

    def make_page_2(char, player):
        def y(a): return a if a else "None"

        page_2 = discord.Embed(description="**Description**:\n"
                                           f"{char['description']}")
        bio = ["race", "background", "alignment", "ethnicity",
               "nationality", "birthplace", "age", "weight",
               "height", "ancestry_and_heritage", "deity", "traits"]

        for i in bio:
            page_2.add_field(name=i.title() + ":", value=y(char[i]))

        if len(char['inventory']) < 65:
            inventory = u.adjust_length(char['inventory'].ljust(65), 1024)
        else:
            inventory = u.adjust_length(char['inventory'], 1024)

        page_2.add_field(name="Inventory:",
                         value=f"```css\n{inventory}```",
                         inline=False)
        page_2.add_field(name="Currency:", value=char['currency'])
        page_2.set_footer(text="Page 2/3")

        if char['image']:
            page_2.set_author(name=char['name'], icon_url=char['image'])
        else:
            page_2.set_author(name=char['name'])

        return page_2

    def make_page_3(char, player):
        def y(a): return a.ljust(65) if len(a) < 65 else a

        page_3 = discord.Embed(description="**Class:** "
                                           f"{char['cclass'].title()}")

        page_3.add_field(name="Spell Attack Roll:",
                         value=char['spell_attack_roll'])
        page_3.add_field(name="Spell DC:", value=char['spell_dc'])
        page_3.add_field(name="Cantrips:",
                         value=f"```css\n{y(char['cantrips'])}```",
                         inline=False),

        for i in range(1, 11):
            slots = (f"Level {i} ({char[f'level_{i}_spell_slots']}/"
                     f"{char[f'maximum_level_{i}_spell_slots']}):")
            spells = f"```css\n{y(char[f'level_{i}_spells'])}```"

            page_3.add_field(name=slots, value=spells, inline=False)
            page_3.set_footer(text="Page 3/3")

        if char['image']:
            page_3.set_author(name=char['name'], icon_url=char['image'])
        else:
            page_3.set_author(name=char['name'])

        return page_3
