import discord as disc
import modules.utility as u
import modules.dnd as dd


file = None  # file will be retrieved later, so it must be provided


# RULES


def rules(ctx, item, info):
    lines = u.adjust_length(info['desc'], 4000).splitlines()
    desc = ""
    subsections = ""
    cursor = 0

    for i in lines:
        if "# " not in i:
            desc += "\n" + i

    embed = disc.Embed(title=f"Rules: {info['name']}",
                       description=desc)

    if "subsections" in info:
        for i in info['subsections']:
            subsections += f"\n{info['subsections'][cursor]['name']}"
            cursor += 1

        embed.add_field(name="Subsections:", value=subsections)

    return embed, file


def rule_sections(ctx, item, info):
    desc = "```markdown\n" + \
        u.adjust_length(info['desc'].replace("***", "**"), 3000) + "```"
    embed = disc.Embed(title=f"Rule Sections: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=desc)

    return embed, file


# CLASSES

def classes(ctx, item, info):
    proficiency_choices = info['proficiency_choices'][0]['from']
    proficiency_list = info['proficiencies']
    saving_throws = info['saving_throws']
    starting_equipment = ""
    prerequisites = ""
    cursor = 0

    for i in info['starting_equipment']:
        quantity = info['starting_equipment'][cursor]['quantity']
        name = info['starting_equipment'][cursor]['equipment']['name']
        starting_equipment += f"{quantity} "
        starting_equipment += f"{name}, "
        cursor += 1

    cursor = 0
    proficiency_options = u.retrieve(proficiency_choices, 'name').replace(
                                   "Skill: ", "")
    base_proficiencies = u.retrieve(proficiency_list, 'name')
    st_proficiencies = u.retrieve(saving_throws, 'name')

    embed = disc.Embed(title=f"Classes: {info['name']}",
                       url=f"https://www.dndbeyond.com/classes/{item}",
                       description=f"The {info['name']} class for the fifth\
                        edition of Dungeons & Dragons.")
    file = disc.File(f"data\\images\\class_tables\\{item}.png",
                     filename="image.png")

    embed.set_image(url="attachment://image.png")
    embed.add_field(name="Hit die:", value=f"d{info['hit_die']}", inline=True)
    embed.add_field(name="Saving Throws:", value=st_proficiencies)

    if 'spellcasting' in info:
        spellcasting_ability = info['spellcasting']['spellcasting_ability']
        ['name']
        embed.add_field(name="Spellcasting Ability:",
                        value=spellcasting_ability['name'])

    embed.add_field(name="Proficiencies:", value=base_proficiencies)
    embed.add_field(name="Proficiency Choices:", value=proficiency_options)

    if 'prerequisites' in info['multi_classing']:
        for i in info['multi_classing']['prerequisites']:
            prerequisites += str(info['multi_classing']['prerequisites']
                                 [cursor]['minimum_score'])
            name = (info['multi_classing']['prerequisites'][cursor]
                    ['ability_score']['name'])
            prerequisites += f" {name}, "
            cursor += 1

        embed.add_field(name='Multiclassing Prerequisites:',
                        value=prerequisites[:-2], inline=False)
        cursor = 0

    else:
        for i in info['multi_classing']['prerequisite_options']['from']:
            prerequisites += str(info['multi_classing']['prerequisite_options']
                                 ['from'][cursor]['minimum_score'])
            name = (info['multi_classing']['prerequisite_options']['from']
                    [cursor]['ability_score']['name'])
            prerequisites += f" {name} or "
            cursor += 1

        embed.add_field(name='Multiclassing Prerequisites:',
                        value=prerequisites[:-3], inline=False)

    if info['multi_classing']['proficiencies']:
        multiclassing_proficiencies = u.retrieve(info['multi_classing']
                                                 ['proficiencies'], 'name')
        embed.add_field(name='Multiclassing Proficiencies:',
                        value=multiclassing_proficiencies, inline=False)
    else:
        embed.add_field(name='Multiclassing Proficiencies:', value="None",
                        inline=False)

    return embed, file


def classes_subclasses(ctx, item, info):
    results = u.retrieve(info['results'], "name")

    embed = disc.Embed(title=f"Subclasses: {item.title()}",
                       description=f"**Matches:** {info['count']}\n**Results:**\
                                    \n{results}")

    return embed, file


def classes_spellcasting(ctx, item, info):
    cursor = 0

    spell_abil = info['spellcasting_ability']['name']
    embed = disc.Embed(title=f"Spellcasting: {item.title()}",
                       description=f"**Spellcasting Ability:** {spell_abil}")

    for i in info['info']:
        embed.add_field(name=info['info'][cursor]['name'],
                        value=u.adjust_length(u.list_to_str(info['info']
                                                            [cursor]['desc'])),
                        inline=False)

        cursor += 1

    return embed, file


def classes_spells(ctx, item, info):

    spells = u.adjust_length(u.retrieve(info['results'], 'name'), 400)

    embed = disc.Embed(title=f'{item.title()} Spells',
                       description=f"**Matches:** {info['count']}\n**Results:**\
                        \n{spells}")

    return embed, file


def classes_features(ctx, item, info):

    features = u.retrieve(info['results'], 'index', '\n')

    embed = disc.Embed(title=f'{item.title()} Features',
                       description=f"**Matches:** {info['count']}\n**Results:**\
                       \n{u.adjust_length(features, 4000)}")

    return embed, file


def classes_proficiencies(ctx, item, info):

    proficiencies = u.adjust_length(u.retrieve(info['results'], 'name'), 4000)

    embed = disc.Embed(title=f'{item.title()} Proficiencies',
                       description=f"**Matches:** {info['count']}\n**Results:**\
                       \n{proficiencies}")

    return embed, file


def classes_multi_classing(ctx, item, info):
    prerequisites = ""
    prerequisite_options = ""
    proficiency_choices = ""
    proficiencies = u.retrieve(info['proficiencies'], 'name')
    cursor = 0
    macro_cursor = 0

    if proficiencies:
        pass
    else:
        proficiencies = "---"

    embed = disc.Embed(title=f"Multiclassing: {item.title()}")
    embed.add_field(name="Proficiencies:", value=proficiencies, inline=False)

    if 'prerequisites' in info:
        for i in info['prerequisites']:
            prerequisite = info['prerequisites'][cursor]['minimum_score']
            name = info['prerequisites'][cursor]['ability_score']['name']
            prerequisites += f"{prerequisite} "
            prerequisites += f"{name}, "
            cursor += 1

        embed.add_field(name="Prerequisites:", value=prerequisites[:-2],
                        inline=False)
    cursor = 0

    if 'prerequisite_options' in info:
        for i in info['prerequisite_options']:
            min_score = (info['prerequisite_options']['from'][macro_cursor]
                         ['minimum_score'])
            name = (info['prerequisite_options']['from'][macro_cursor]
                    ['ability_score']['name'])
            prerequisite_options += f"{min_score} "
            prerequisite_options += f"{name}, "
            cursor += 1

        choose = info['prerequisite_options']['choose']
        embed.add_field(name=f"Prerequisite Options (choose {choose}):",
                        value=prerequisite_options[:-2], inline=False)
    cursor = 0

    if 'proficiency_choices' in info:
        for i in info['proficiency_choices']:
            name = (info['proficiency_choices'][macro_cursor]['from'][cursor]
                    ['name'])
            proficiency_choices += f"{name}, "
            cursor += 1

        choose = info['proficiency_choices'][0]['choose']
        embed.add_field(name=f"Proficiency Options (choose {choose}):",
                        value=proficiency_choices[:-2], inline=False)

    return embed, file


def classes_levels(ctx, item, info):

    embed = disc.Embed(title=F"Levels: {info[0]['class']['name']}")
    file = disc.File(f"data\\images\\class_tables\\{item}.png",
                     filename="image.png")
    embed.set_image(url="attachment://image.png")

    return embed, file


def classes_levels_(ctx, item, info, level):

    features = u.retrieve(info['features'], 'name')
    if features:
        pass
    else:
        features = "---"

    embed = disc.Embed(title=f"Levels: {info['class']['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=f"**Level:** {info['level']}")

    embed.add_field(name="Proficiency Bonus:", value=info['prof_bonus'],
                    inline=False)

    embed.add_field(name="Features:", value=features, inline=False)

    if "spellcasting" in info:
        spellcasting = u.dict_to_str(info['spellcasting'], modifier="\n")
        embed.add_field(name="Spellcasting:", value=spellcasting, inline=False)

    if "class_specific" in info:
        class_specific = u.dict_to_str(info['class_specific'], modifier="\n")
        embed.add_field(name="Class Specific:", value=class_specific,
                        inline=False)

    return embed, file


def classes_levels_spells(ctx, item, info, level):

    results = ""
    cursor = 0

    for i in info['results']:
        results += f"{info['results'][cursor]['name']}\n"
        cursor += 1

    results = u.adjust_length(results, 4000)
    embed = disc.Embed(title=f"Spells: {item.title()} {level}",
                       description=f"**Matches:** {info['count']}\n**Results:**\
                       \n{results}")

    return embed, file


def subclasses(ctx, item, info):

    embed = disc.Embed(title=f"Subclasses: {info['name']}",
                       description=f"**Class:** {info['class']['name']}")
    embed.add_field(name=info['subclass_flavor'],
                    value=u.list_to_str(info['desc']))

    # NEED TO ADD SPELLS

    return embed, file


def subclasses_features(ctx, item, info):
    results = ""
    cursor = 0

    for i in info['results']:
        results += f"{info['results'][cursor]['index']}\n"
        cursor += 1

    results = u.adjust_length(results, 4000)
    embed = disc.Embed(title=f"Features: {item.title()}",
                       description=f"**Matches:** {info['count']}\n**Results:**\
                       \n{results}")

    return embed, file


def subclasses_levels(ctx, item, info):
    description = ""
    cursor = 0

    embed = disc.Embed(title=f"Levels: {item.title()}",
                       description=f"**Class:** {info[0]['class']['name']}")

    for i in info:
        title = f"Level {info[cursor]['level']}:"
        description = u.retrieve(info[cursor]['features'], 'name')

        if description:
            embed.add_field(name=title, value=description, inline=False)

        else:
            pass

        cursor += 1

    return embed, file


def subclasses_levels_(ctx, item, info, level):

    features = u.list_to_str(u.retrieve(info['features'], 'name'))

    embed = disc.Embed(title=F"Levels: {item.title()} {level}",
                       description=f"**Features:**\n{features}")

    return embed, file


# ADDITIONAL DATA

def races(ctx, item, info):
    """Takes a json file's contents, builds a race embed, and returns it."""

    ability_increase = ""
    cursor = 0
    traits = u.retrieve(info['traits'], 'name')
    subraces = u.retrieve(info['subraces'], 'name')

    for i in info['ability_bonuses']:
        bonus = info['ability_bonuses'][cursor]['bonus']
        name = info['ability_bonuses'][cursor]['ability_score']['name']
        ability_increase += f"+{bonus}"
        ability_increase += f" {name} "
        cursor += 1

    embed = disc.Embed(title=f"Races: {info['name']}",
                       url=f'https://www.dndbeyond.com/races/{item}',
                       description=f"The {info['name']} race for the fifth \
                       edition of Dungeons & Dragons.")
    embed.add_field(name='Speed: ', value=f"{info['speed']}ft.")
    embed.add_field(name='Size: ', value=info['size'])
    embed.add_field(name='Ability Score Increase:', value=ability_increase)
    embed.add_field(name='Age:', value=info['age'], inline=False)
    embed.add_field(name='Alignment:', value=info['alignment'], inline=False)

    if info['starting_proficiencies']:
        starting_proficiencies = u.retrieve(info['starting_proficiencies'],
                                            'name')
        embed.add_field(name='Proficiencies:',
                        value=starting_proficiencies.replace("Skill:", ""))

    if 'starting_proficiency_options' in info:
        proficiency_options = u.retrieve(info["starting_proficiency_options"]
                                         ['from'], 'name').replace("Skill: ",
                                                                   "")
        choose = info['starting_proficiency_options']['choose']
        embed.add_field(name=f'Proficiency Options(choose {choose}):',
                        value=proficiency_options)

    if traits:
        embed.add_field(name='Traits:', value=traits)

    embed.add_field(name="Languages", value=info['language_desc'],
                    inline=False)

    if subraces:
        embed.add_field(name='Subraces:', value=subraces)

    return embed, file


def subraces(ctx, item, info):
    ability_bonuses = ""
    cursor = 0

    for i in info['ability_bonuses']:
        ability_bonuses += f"+ {info['ability_bonuses'][cursor]['bonus']}\
        {info['ability_bonuses'][cursor]['ability_score']['name']}\n"
        cursor += 1
    cursor = 0

    if info['starting_proficiencies']:
        starting_proficiencies = ""
        for i in info['starting_proficiencies']:
            starting_proficiencies += i['name'] + ", "

    desc = f"{info['race']['name']}\n{info['desc']}"
    embed = disc.Embed(title=f"Subraces: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=f"**Race:** {desc}")
    embed.add_field(name="Ability Bonuses:", value=ability_bonuses,
                    inline=False)
    embed.add_field(name="Starting Proficiencies:",
                    value=starting_proficiencies[:-2] if
                    info['starting_proficiencies'] else None, inline=False)
    embed.add_field(name="Racial Traits:",
                    value=u.retrieve(info['racial_traits'], 'name'),
                    inline=False)
    if 'language_options' in info:
        choose = info['language_options']['choose']
        name = u.retrieve(info['language_options']['from'], 'name')
        embed.add_field(name=f"Languague Options (choose {choose}):",
                        value=name, inline=False)

    return embed, file


def traits(ctx, item, info):
    proficiencies = ""
    cursor = 0

    embed = disc.Embed(title=f"Traits: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=u.list_to_str(info['desc']))

    if info['races']:
        races = u.retrieve(info['races'], 'name')
        embed.add_field(name="Races:", value=races, inline=False)

    if info['subraces']:
        subraces = u.retrieve(info['subraces'], 'name')
        embed.add_field(name="Races:", value=subraces, inline=False)

    if info['proficiencies']:
        for i in info['proficiencies']:
            proficiencies += info['proficiencies'][cursor]['name']
            cursor += 1

        embed.add_field(name="Proficiencies:", value=proficiencies,
                        inline=False)

    if 'proficiency_choices' in info:
        type = f"{info['proficiency_choices']['type'].title()}\n\
                {u.retrieve(info['proficiency_choices']['from'], 'name')}"
        embed.add_field(name=f"Proficiency Choices (choose \
                        {info['proficiency_choices']['choose']}):",
                        value=f"**Type:** {type}", inline=False)

    if 'trait_specific' in info:
        embed.add_field(name="Breath Weapon:",
                        value=f"**Damage Type:** {type}", inline=False)

    return embed, file


def spells(ctx, item, info):
    """Takes a json file's contents, builds a spell embed, and returns it."""

    higher_level = ""
    components = u.list_to_str(info['components'])

    if info['level'] == 0:
        level_denominator = 'Cantrip'
    elif info['level'] == 1:
        level_denominator = "1st level"
    elif info['level'] == 2:
        level_denominator = "2nd level"
    elif info['level'] == 3:
        level_denominator = "3rd level"
    else:
        level_denominator = str(info['level']) + 'th level'

    if info['ritual']:
        description = f"{level_denominator} {info['school']['name']}\
                      (ritual).\n"
    else:
        description = f"{level_denominator} {info['school']['name']}.\n"

    for i in info['desc']:
        description += f" {i}"

    desc = description.replace("['" and '"]', "")
    embed = disc.Embed(title=f"Spells: {info['name']}",
                       url=f"https://www.dndbeyond.com/spells/{item}",
                       description=f"*{desc}*")
    embed.add_field(name='Casting Time:', value=info['casting_time'])

    if info['concentration']:
        embed.add_field(name='Duration:', value="Concentration, " +
                        info['duration'].lower())
    else:
        embed.add_field(name='Duration:', value=info['duration'])
    embed.add_field(name='Range:', value=info['range'])

    if 'material' in info:
        embed.add_field(name='Components:', value=f"{components}\n\
                        {info['material']}")
    else:
        embed.add_field(name='Components:', value=components)

    if 'higher_level' in info:
        for i in info['higher_level']:
            higher_level += f" {i}"
        embed.add_field(name="At Higher Levels:",
                        value=higher_level.replace("['" and '"]', ""),
                        inline=False)

    return embed, file


def features(ctx, item, info):

    description = u.list_to_str(info['desc'])

    embed = disc.Embed(title=f"Features: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=u.adjust_length(f"*Level {info['level']} {info['class']['name']} \
                       feature.*\n{description}", 4000))

    return embed, file


def backgrounds(ctx, item, info):

    starting_proficiencies = u.retrieve(info['starting_proficiencies'], 'name')
    languague_options = u.retrieve(info['language_options']['from'], 'name')
    choose = info['language_options']['choose']
    desc = u.adjust_length(u.list_to_str(info['feature']['desc']))

    embed = disc.Embed(title=f"Backgrounds: {info['name']}",
                       url=f"https://www.dndbeyond.com/backgrounds/{item}",
                       description=desc)

    embed.add_field(name='Feature:', value=info['feature']['name'])
    embed.add_field(name='Starting Proficiencies:',
                    value=starting_proficiencies.replace("Skill:", ""))
    embed.add_field(name=f"Language Options (choose {choose}):",
                    value=languague_options, inline=False)
    embed.add_field(name="Starting Equipment:",
                    value="1 Clothes, common; 1 pouch")
    embed.add_field(name="Starting Equipment Options (choose 1):",
                    value="Holy Symbols")
    return embed, file


def feats(ctx, item, info):
    prerequisites = str(info['prerequisites'][0]['minimum_score'])
    prerequisites += f" {info['prerequisites'][0]['ability_score']['name']}"
    description = u.adjust_length(u.list_to_str(info['desc']))

    embed = disc.Embed(title=f"Feats: {info['name']}",
                       url=f"https://www.dndbeyond.com/feats/{item}",
                       description=description)
    embed.add_field(name="Prerequisites:", value=prerequisites)

    return embed, file


# MONSTERS

def monsters(ctx, item, info):
    speed = ""
    proficiencies = ""
    saving_throws = ""
    special_abilities = ""
    actions = ""
    legendary_actions = ""
    cursor = 1
    stats = "```css\n"
    stats_label = ""

    if 'walk' in info['speed']:
        speed += f"\n{info['speed']['walk']}"

    if 'swim' in info['speed']:
        speed += f"\nSwim: {info['speed']['swim']}"

    if 'fly' in info['speed']:
        speed += f"\nFly: {info['speed']['fly']}"

    if 'climb' in info['speed']:
        speed += f"\nClimb: {info['speed']['climb']}"

    if 'burrow' in info['speed']:
        speed += f"\nBurrow: {info['speed']['burrow']}"

    for i in ["strength", "dexterity", "constitution", "intelligence",
              "wisdom", "charisma"]:
        stat = dd.get_modifier(info[i])
        stats_label = stats_label.ljust(12*cursor) + f"{i[:3].upper()}"

        stats = stats.ljust(10*cursor) + f"{info[i]}({stat})"
        cursor += 1

    stats = stats + "```".ljust(80)
    stats_label = "```" + stats_label[7:].ljust(74) + "```"
    desc = f"{info['size']} {info['type']}, {info['alignment']}"
    cursor = 0

    embed = disc.Embed(title=f"Monsters: {info['name']}",
                       url=f"https://www.dndbeyond.com/monsters/{item}",
                       description=desc)
    embed.add_field(name="Hit Points:",
                    value=f"{info['hit_points']} ({info['hit_dice']})")
    embed.add_field(name="Armor Class:", value=info['armor_class'])
    embed.add_field(name="Speed:", value=speed)
    embed.add_field(name=stats_label, value=stats, inline=False)

    if 'proficiencies' in info:
        for i in info['proficiencies']:
            name = info['proficiencies'][cursor]['proficiency']['name']
            value = info['proficiencies'][cursor]['value']
            if "Saving Throw:" in name:
                saving_throws += name.replace("Saving Throw:", "")
                saving_throws += f" +{value}; "

            else:
                proficiencies += name.replace("Skill:", "")
                proficiencies += f" +{value}; "

            cursor += 1

        if saving_throws:
            embed.add_field(name="Saving Throws:", value=saving_throws,
                            inline=False)
        if proficiencies:
            embed.add_field(name="Proficiencies:", value=proficiencies,
                            inline=False)

    embed.add_field(name="Senses:", value=u.dict_to_str(info['senses']),
                    inline=False)
    cursor = 0

    if info['damage_vulnerabilities']:
        damage_vulnerabilities = u.list_to_str(info['damage_vulnerabilities'],
                                               "\n")
        embed.add_field(name="Damage Vulnerabilities:",
                        value=damage_vulnerabilities)

    if info['damage_resistances']:
        damage_resistances = u.list_to_str(info['damage_resistances'], "\n")
        embed.add_field(name="Damage Resistances:", value=damage_resistances)

    if info['damage_immunities']:
        damage_immunities = u.list_to_str(info['damage_immunities'], "\n")
        embed.add_field(name="Damage Immunities:", value=damage_immunities)

    if info['condition_immunities']:
        condition_immunities = u.list_to_str(u.retrieve(
                                             info['condition_immunities'],
                                             'name'))

        embed.add_field(name="Condition Immunities:",
                        value=condition_immunities)

    if info['languages']:
        embed.add_field(name='Languages:',
                        value=info['languages'].capitalize(),
                        inline=False)

    embed.add_field(name='Challenge Rating:', value=info['challenge_rating'],
                    inline=False)

    if 'special_abilities' in info:
        for i in info['special_abilities']:
            name = info['special_abilities'][cursor]['name']
            desc = info['special_abilities'][cursor]['desc']
            special_abilities += f"\n**{name}:** "
            special_abilities += desc
            cursor += 1

        embed.add_field(name='Special Abilities:',
                        value=u.adjust_length(special_abilities), inline=False)
        cursor = 0

    if 'actions' in info:
        for i in info['actions']:
            actions += f"\n**{info['actions'][cursor]['name']}:** "
            actions += info['actions'][cursor]['desc']
            cursor += 1

        actions = [actions[i:i+1000] for i in range(0, len(actions), 1000)]

        for i in actions:
            if i != actions[0]:
                embed.add_field(name='\u200b', value=i,
                                inline=False)
            else:
                embed.add_field(name='Actions:', value=i,
                                inline=False)
        cursor = 0

    if 'legendary_actions' in info:
        for i in info['legendary_actions']:
            name = info['legendary_actions'][cursor]['name']
            desc = info['legendary_actions'][cursor]['desc']
            legendary_actions += f"\n**{name}:** "
            legendary_actions += desc
            cursor += 1

        embed.add_field(name='Legendary Actions:',
                        value=u.adjust_length(legendary_actions), inline=False)
        cursor = 0

    return embed, file


# ITEMS

def equipment_categories(ctx, item, info):

    equipment = u.retrieve(info['equipment'], 'name')

    embed = disc.Embed(title=f"Equipment Categories: {info['name']}",
                       description=u.adjust_length(equipment))

    return embed, file


def equipment(ctx, item, info):

    if info['equipment_category']['name'] == "Weapon":
        properties = u.retrieve(info['properties'], "name").replace(", Monk",
                                                                    "")

        embed = disc.Embed(title=f"Equipment: {info['name']}",
                           url=f"https://www.dndbeyond.com/equipment/{item}",
                           description=f"{info['category_range']} Weapon")

        embed.add_field(name='Damage:', value=f"{info['damage']['damage_dice']}\
                        {info['damage']['damage_type']['name']}",
                        inline=False)

        if info['range']['long']:
            embed.add_field(name="Range:",
                            value=f"{info['range']['normal']} ft., \
                            {info['range']['long']} ft.",
                            inline=False)

        else:
            embed.add_field(name="Range:",
                            value=f"{info['range']['normal']} ft.",
                            inline=False)

        embed.add_field(name="Properties:", value=properties, inline=False)
        embed.add_field(name="Cost:", value=f"{info['cost']['quantity']}\
                        {info['cost']['unit']}")
        embed.add_field(name="Weight:", value=info['weight'])

    elif info['equipment_category']['name'] == "Armor":
        embed = disc.Embed(title=info['name'],
                           url=f"https://www.dndbeyond.com/equipment/{item}",
                           description=f"{info['armor_category']} Armor")

        if info['armor_class']['dex_bonus']:
            if info['armor_class']['max_bonus']:
                embed.add_field(name="Armor Class:",
                                value=f"{info['armor_class']['base']} + DEX (\
                                max {info['armor_class']['max_bonus']})")
            else:
                embed.add_field(name="Armor Class:",
                                value=f"{info['armor_class']['base']} + DEX")
        else:
            embed.add_field(name="Armor Class:",
                            value=info['armor_class']['base'])

        if info['str_minimum'] > 0:
            embed.add_field(name="Strength:", value=info['str_minimum'])
        else:
            embed.add_field(name="Strength:", value='---')

        if info['stealth_disadvantage']:
            embed.add_field(name="Stealth:", value="Disadvantage")
        else:
            embed.add_field(name="Stealth", value="---")

        embed.add_field(name="Cost:", value=f"{info['cost']['quantity']} \
                        {info['cost']['unit']}")
        embed.add_field(name="Weight:", value=info['weight'])

    elif info['equipment_category']['name'] == "Adventuring Gear":
        if info['gear_category']['name'] == "Equipment Packs":
            items = ""
            cursor = 0
            description = (f"**Type:** {info['gear_category']['name']}\n"
                           f"**Items:**\n{items}")

            for i in info['contents']:
                items += f"- {info['contents'][cursor]['quantity']} "
                items += f"{info['contents'][cursor]['item']['name']}\n"
                cursor += 1

            embed = disc.Embed(title=f"Equipment: {info['name']}",
                               url=(f"https://www.dndbeyond.com/equipment/"
                                    f"{item}"),
                               description=description)

            if "cost" in info:
                embed.add_field(name="Cost:",
                                value=(f"{info['cost']['quantity']} "
                                       f"{info['cost']['unit']}"))

        else:
            if 'desc' in info:
                description = (f"{info['gear_category']['name']}\n"
                               f"{u.list_to_str(info['desc'])}")
                embed = disc.Embed(title=f"Equipment: {info['name']}",
                                   url=(f"https://www.dndbeyond.com/equipment/"
                                        f"{item}"),
                                   description=description)
            else:
                description = f"{info['gear_category']['name']}"
                embed = disc.Embed(title=f"Equipment: {info['name']}",
                                   url=(f"https://www.dndbeyond.com/equipment/"
                                        f"{item}"),
                                   description=description)

            embed.add_field(name="Cost:",
                            value=(f"{info['cost']['quantity']} "
                                   f"{info['cost']['unit']}"))
            embed.add_field(name="Weight:", value=info['weight'])

    elif info['equipment_category']['name'] == "Tools":
        embed = disc.Embed(title=f"Equipment: {info['name']}",
                           url=f"https://www.dndbeyond.com/equipment/{item}",
                           description=(f"{info['tool_category']}\n"
                                        f"{u.list_to_str(info['desc'])}"))

        embed.add_field(name="Cost:",
                        value=(f"{info['cost']['quantity']} "
                               f"{info['cost']['unit']}"))
        embed.add_field(name="Weight:", value=info['weight'])

    elif info['equipment_category']['name'] == "Mounts and Vehicles":
        if 'desc' in info:
            description = (f"{info['equipment_category']['name']}\n"
                           f"{u.list_to_str(info['desc'])}")
            embed = disc.Embed(title=f"Equipment: {info['name']}",
                               url=(f"https://www.dndbeyond.com/equipment/"
                                    f"{item}"),
                               description=description)

            if "speed" in info:
                embed.add_field(name="Speed:",
                                value=(f"{info['speed']['quantity']} "
                                       f"{info['speed']['unit']}"),
                                inline=False)

            if "capacity" in info:
                embed.add_field(name="Capacity:", value=info['capacity'],
                                inline=False)

            embed.add_field(name="Cost:",
                            value=(f"{info['cost']['quantity']} "
                                   f"{info['cost']['unit']}"))

            if "weight" in info:
                embed.add_field(name="Weight:", value=info['weight'])

        else:
            description = f"{info['equipment_category']['name']}"
            embed = disc.Embed(title=f"Equipment: {info['name']}",
                               url=(f"https://www.dndbeyond.com/equipment/"
                                    f"{item}"),
                               description=description)

            if "speed" in info:
                embed.add_field(name="Speed:",
                                value=(f"{info['speed']['quantity']} "
                                       f"{info['speed']['unit']}"),
                                inline=False)

            if "capacity" in info:
                embed.add_field(name="Capacity:", value=info['capacity'],
                                inline=False)

            embed.add_field(name="Cost:",
                            value=(f"{info['cost']['quantity']} "
                                   f"{info['cost']['unit']}"))

            if "weight" in info:
                embed.add_field(name="Weight:", value=info['weight'])

    return embed, file


def magic_items(ctx, item, info):

    description = ""
    first = True

    for i in info['desc']:
        if first:
            description += f"*{i}*\n"
            first = False

        else:
            description += f"{i}\n"

    embed = disc.Embed(title=f"Magic Items: {info['name']}",
                       url=f"https://www.dndbeyond.com/magic-items/{item}",
                       description=u.adjust_length(description, 4000))

    return embed, file


# GAME MECHANICS


def conditions(ctx, item, info):
    description = u.list_to_str(info['desc'])

    embed = disc.Embed(title=f"Conditions: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=description)

    return embed, file


def damage_types(ctx, item, info):
    description = u.list_to_str(info['desc'])

    embed = disc.Embed(title=f"Damage Types: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=description)

    return embed, file


def magic_schools(ctx, item, info):

    embed = disc.Embed(title=f"Magic Schools: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=info['desc'])

    return embed, file


# CHARACTER DATA (MOVE UP)


def ability_scores(ctx, item, info):
    description = u.list_to_str(info['desc'])
    skills = u.retrieve(info['skills'], 'name')

    embed = disc.Embed(title=f"Ability Scores: {info['full_name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=description)
    embed.add_field(name="Skills:", value=skills)

    return embed, file


def skills(ctx, item, info):
    description = u.list_to_str(info['desc'])

    embed = disc.Embed(title=f"Skills: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=description)
    embed.add_field(name="Ability Score:", value=info['ability_score']['name'])

    return embed, file


def proficiencies(ctx, item, info):
    classes = u.retrieve(info['classes'], 'name')
    races = u.retrieve(info['races'], 'name')

    embed = disc.Embed(title=f"Proficiencies: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=f"Type: {info['type']}")

    if races:
        embed.add_field(name="Races: ", value=races)

    if classes:
        embed.add_field(name="Classes:", value=classes)

    return embed, file


def languages(ctx, item, info):
    typical_speakers = ""

    for i in info['typical_speakers']:
        typical_speakers += f"{i}, "

    embed = disc.Embed(title=f"Languages: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}")
    embed.add_field(name="Type:", value=info['type'])
    embed.add_field(name="Script:", value=info['script'])
    embed.add_field(name="Typical Speakers:", value=typical_speakers[:-2])

    return embed, file


def alignments(ctx, item, info):

    embed = disc.Embed(title=f"Alignments: {info['name']}",
                       url=f"https://www.dnd5eapi.co{info['url']}",
                       description=info['desc'])

    return embed, file
