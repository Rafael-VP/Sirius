import math


levels = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000
}

classes_saving_throws = {
    "barbarian": "STR, CON",
    "bard": "DEX, CHA",
    "cleric": "WIS, CHA",
    "druid": "INT, WIS",
    "fighter": "STR, CON",
    "monk": "STR, DEX",
    "paladin": "WIS, CHA",
    "ranger": "STR, DEX",
    "rogue": "DEX, INT",
    "sorcerer": "CON, CHA",
    "warlock": "WIS, CHA",
    "wizard": "INT, WIS"
}


def get_modifier(number):
    """u.retrieves the modifier equivalent for any given number as a string."""

    output = (int(number) - 10) / 2
    output = math.floor(output)
    if output >= 0:
        output = "+" + str(output)

    return output


def get_proficiency_bonus(level):
    """Gets the corresponding proficiency bonus for a given level. An equation is
    used for level +20 support."""
    level = int(level)

    if 1 <= level <= 4:
        output = 2

    elif 5 <= level <= 8:
        output = 3

    elif 9 <= level <= 12:
        output = 4

    elif 13 <= level <= 16:
        output = 5

    elif 17 <= level <= 20:
        output = 6

    else:
        try:
            output = math.floor((int(level) + 2) / 4)
        except Exception:
            output = "None"

    return output


def get_experience(level):
    """Returns the corresponding experience for a given level."""

    if level in levels:
        experience = levels[level]
    else:
        experience = 0

    return experience


def get_level(exp):
    if 0 < exp < 300:
        level = 1
    elif 300 <= exp < 900:
        level = 2
    elif 900 <= exp < 2700:
        level = 3
    elif 2700 <= exp < 6500:
        level = 4
    elif 6500 <= exp < 14000:
        level = 5
    elif 14000 <= exp < 23000:
        level = 6
    elif 23000 <= exp < 34000:
        level = 7
    elif 34000 <= exp < 48000:
        level = 8
    elif 48000 <= exp < 64000:
        level = 9
    elif 64000 <= exp < 85000:
        level = 10
    elif 85000 <= exp < 100000:
        level = 11
    elif 100000 <= exp < 120000:
        level = 12
    elif 120000 <= exp < 140000:
        level = 13
    elif 140000 <= exp < 165000:
        level = 14
    elif 165000 <= exp < 195000:
        level = 15
    elif 195000 <= exp < 225000:
        level = 16
    elif 225000 <= exp < 265000:
        level = 17
    elif 265000 <= exp < 305000:
        level = 18
    elif 305000 <= exp < 355000:
        level = 19
    elif 355000 < exp:
        level = 20

    return level


def get_hit_die(cclass, hit_die):
    """Determines D&D 5e character's hit dice type based on the chosen
    class."""

    classes_hit_dice = dict.fromkeys(['sorcerer', 'wizard'], 6)
    classes_hit_dice.update(dict.fromkeys(['bard', 'cleric', 'druid',
                                           'monk', 'rogue', 'warlock'], 8))
    classes_hit_dice.update(dict.fromkeys(['fighter', 'paladin', 'ranger'],
                                          10))
    classes_hit_dice.update(dict.fromkeys(['barbarian'], 12))

    if cclass in classes_hit_dice:
        hit_die = classes_hit_dice[cclass]
    else:
        if not hit_die:
            hit_die = 6

    return hit_die


def get_saving_throws(cclass, saving_throws):
    if cclass in classes_saving_throws:
        saving_throws = classes_saving_throws[cclass]
    else:
        if not saving_throws:
            saving_throws = "None"

    return saving_throws
