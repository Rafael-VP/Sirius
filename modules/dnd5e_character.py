import modules.dnd as dd
import modules.utility as u
import discord


stats_skills = {
    "STR": ["athletics"],
    "DEX": ["acrobatics", "sleight_of_hand", "stealth"],
    "INT": ["arcana", "history", "investigation", "nature", "religion"],
    "WIS": ["animal_handling", "insight", "medicine", "perception",
            "survival"],
    "CHA": ["deception", "intimidation", "performance", "persuasion"]
}


class DnD5e_Character:
    """Holds attribute values for a Dungeons & Dragons 5th Edition character
    sheet. New instances have their saving throws and hit dice automatically
    assigned based on their choosen class. The instance is then passed through
    the character encoder and becomes json serializable for database
    storage."""

    def __init__(self, name, cclass, level):

        self.system = "D&D 5e"
        self.image = ("https://publicdomainvectors.org/photos/abstract-user-"
                      "flat-1.png")
        self.name = name
        self.cclass = cclass
        self.level = level
        self.race = "None"
        self.background = "None"
        self.alignment = "None"
        self.experience = dd.get_experience(level)
        self.proficiency_bonus = dd.get_proficiency_bonus(self.level)

        self.saving_throws = dd.get_saving_throws(self.cclass, None)
        self.features = "None"
        self.proficiencies = "None"

        self.armor_class = 10
        self.initiative = 0
        self.speed = "30 ft."

        self.inventory = ""
        self.currency = 0

        self.age = "None"
        self.height = "None"
        self.weight = "None"
        self.eyes = "None"
        self.skin = "None"
        self.hair = "None"

        self.description = "None"

        self.spellcasting_ability = "None"
        self.spell_save_dc = "None"
        self.spell_attack_bonus = "None"

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

        self.hit_points = dd.get_hit_die(self.cclass, None)
        self.maximum_hit_points = dd.get_hit_die(self.cclass, None)
        self.temporary_hit_points = 0
        self.hit_die = dd.get_hit_die(self.cclass, None)
        self.hit_dice = level
        self.death_saves_successes = 0
        self.death_saves_failures = 0

        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.charisma = 10

        self.athletics_proficiency = False
        self.athletics = 0
        self.acrobatics_proficiency = False
        self.acrobatics = 0
        self.sleight_of_hand_proficiency = False
        self.sleight_of_hand = 0
        self.stealth_proficiency = False
        self.stealth = 0
        self.arcana_proficiency = False
        self.arcana = 0
        self.history_proficiency = False
        self.history = 0
        self.investigation_proficiency = False
        self.investigation = 0
        self.nature_proficiency = False
        self.nature = 0
        self.religion_proficiency = False
        self.religion = 0
        self.animal_handling_proficiency = False
        self.animal_handling = 0
        self.insight_proficiency = False
        self.insight = 0
        self.medicine_proficiency = False
        self.medicine = 0
        self.perception_proficiency = False
        self.perception = 0
        self.survival_proficiency = False
        self.survival = 0
        self.deception_proficiency = False
        self.deception = 0
        self.intimidation_proficiency = False
        self.intimidation = 0
        self.performance_proficiency = False
        self.performance = 0
        self.persuasion_proficiency = False
        self.persuasion = 0

        self.passive_perception = 10

    def make_page_1(char, player):
        """Embed builder function for the first page of the Dungeons & Dragons 5th
        Edition character sheet. Modifiers are calculated automatically in
        accordance to base stats."""
        def x(a): return "🗹" if a else "☐"
        def y(a): return a if a else "None"
        def z(a): return f"+{a}" if int(a) > 0 else a

        proficiency_bonus = dd.get_proficiency_bonus(char['level'])
        skills_field = "```css\n"
        cursor = 1
        stats = "```css\n"
        stats_label = ""

        for i in ["strength", "dexterity", "constitution", "intelligence",
                  "wisdom", "charisma"]:
            stat = dd.get_modifier(char[i])
            stats_label = stats_label.ljust(12*cursor) + f"{i[:3].upper()}"

            stats = stats.ljust(10*cursor) + f"{char[i]}({stat})"
            cursor += 1

        stats = stats + "```".ljust(80)
        stats_label = "```" + stats_label[7:].ljust(74) + "```"

        page_1 = discord.Embed(description=f"**Player:** {player}")
        page_1.add_field(name="Class:", value=char['cclass'].title())
        page_1.add_field(name="Level:",
                         value=f"{char['level']} ({char['experience']} exp.)")
        page_1.add_field(name="Proficiency Bonus:",
                         value=f"+{proficiency_bonus}")
        page_1.add_field(name=stats_label, value=stats, inline=False)
        page_1.add_field(name="Armor Class:", value=char['armor_class'])
        page_1.add_field(name='Initiative:', value=char['initiative'])
        page_1.add_field(name='Speed:', value=char['speed'])
        page_1.add_field(name="Hit Points:",
                         value=(f"{char['hit_points']} / "
                                f"{char['maximum_hit_points']}"))
        page_1.add_field(name='Temporary Hit Points:',
                         value=char['temporary_hit_points'])
        page_1.add_field(name="Hit Dice:",
                         value=f"{char['hit_dice']}d{char['hit_die']}\u200b")
        page_1.add_field(name="Death Saves:",
                         value=f"Successes: {char['death_saves_successes']}"
                               f"\nFailures: {char['death_saves_failures']}")
        page_1.add_field(name="Saving Throws:",
                         value=y(char['saving_throws']))
        page_1.add_field(name="Passive Perception:",
                         value=y(char['passive_perception']))

        for i in ["acrobatics", "animal_handling", "arcana", "athletics",
                  "deception", "history", "insight", "intimidation",
                  "investigation", "medicine", "nature", "perception",
                  "performance", "persuasion", "religion", "sleight_of_hand",
                  "stealth", "survival"]:
            skill = "None"

            for key, value in stats_skills.items():
                for s in value:
                    if s == i:
                        skill = key

            skills_field += (f"{x(char[f'{i}_proficiency'])} "
                             f"{i.title().replace('_', ' ')} "
                             f"({skill}):".ljust(30) +
                             f"{z(char[i])}\n".rjust(5))

        skills_field = skills_field + "```"

        page_1.add_field(name="Skills", value=skills_field)
        page_1.add_field(name="Features:", value=f"{y(char['features'])}")
        page_1.add_field(name="Proficiencies:",
                         value=f"{char['proficiencies']}\u200b", inline=False)
        page_1.set_footer(text="Page 1/3")

        if char['image']:
            page_1.set_author(name=char['name'], icon_url=char['image'])
        else:
            page_1.set_author(name=char['name'])

        return page_1

    def make_page_2(char):
        """Embed builder function for the second page of the Dungeons & Dragons 5th
        Edition character sheet."""
        def y(a): return a if a else "None"

        if len(char['inventory']) < 65:
            inventory = u.adjust_length(char['inventory'].ljust(65), 1024)
        else:
            inventory = u.adjust_length(char['inventory'], 1024)

        page_2 = discord.Embed(description=("**Description:**"
                                            f"\n{char['description']}"))
        page_2.add_field(name="Race:", value=y(char['race']))
        page_2.add_field(name="Background:",
                         value=y(char['background']))
        page_2.add_field(name="Alignment:", value=y(char['alignment']))
        page_2.add_field(name="Age:", value=y(char['age']))
        page_2.add_field(name="Height:", value=y(char['height']))
        page_2.add_field(name="Weight:", value=y(char['weight']))
        page_2.add_field(name="Eyes:", value=y(char['eyes']))
        page_2.add_field(name="Skin:", value=y(char['skin']))
        page_2.add_field(name="Hair:", value=y(char['hair']))
        page_2.add_field(name="Inventory:", value=f"```css\n{inventory}```",
                         inline=False)
        page_2.add_field(name="Currency:", value=char['currency'])
        page_2.set_footer(text="Page 2/3")

        if char['image']:
            page_2.set_author(name=char['name'], icon_url=char['image'])
        else:
            page_2.set_author(name=char['name'])

        return page_2

    def make_page_3(char):
        """Embed builder function for the third page of the Dungeons & Dragons 5th
        Edition character sheet."""
        def x(a): return a.ljust(65) if len(a) < 65 else a
        def y(a): return a if a else "None"

        page_3 = discord.Embed(description=("**Class: **"
                                            f"{char['cclass'].title()}"))
        page_3.add_field(name="Spellcasting Ability:",
                         value=f"{y(char['spellcasting_ability'])}")
        page_3.add_field(name="Spell Save DC:",
                         value=f"{y(char['spell_save_dc'])}")
        page_3.add_field(name="Spell Attack Bonus:",
                         value=f"{y(char['spell_attack_bonus'])}")
        page_3.add_field(name="Cantrips:",
                         value=f"```css\n{x(char['cantrips'])}```",
                         inline=False)

        for i in range(1, 10):
            slots = (f"Level {i} ({char[f'level_{i}_spell_slots']}/"
                     f"{char[f'maximum_level_{i}_spell_slots']}):")
            spells = f"```css\n{x(char[f'level_{i}_spells'])}```"

            page_3.add_field(name=slots, value=spells, inline=False)
            page_3.set_footer(text="Page 3/3")

        if char['image']:
            page_3.set_author(name=f"{char['system']} {char['name']}",
                              icon_url=char['image'])
        else:
            page_3.set_author(name=f"{char['system']} {char['name']}")

        return page_3
