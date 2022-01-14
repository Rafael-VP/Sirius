def retrieve(list_path, parameter, modifier=","):
    """Retrieves multiple instances of a parameter on a given subdictionary
    and appends all of them to the end of the same string.
    ex.: proficiency_choices[0]['from']"""

    cursor = 0
    item_list = ""

    for i in list_path:
        name = list_path[cursor][parameter]

        if cursor > 0:
            item_list += f"{modifier} {name}"
        else:
            item_list += f"{name}"

        cursor += 1

    return item_list


def adjust_length(string, value=1020):
    """Splits any string longer than 1020 characters and appends an elipsis to
    the end of it. Value can be customized"""

    adjusted_string = (string[:value] + '...') if len(string) > value\
        else string
    return adjusted_string


def list_to_str(input_list, modifier=""):
    """Converts any list to a string cointaining all of its components."""
    output_string = ""

    for i in input_list:
        output_string += f"{modifier}{i}"

    return output_string


def dict_to_str(input_dict, modifier=";"):
    """Retrieves every item in a dictionary and appends it to the end of a
    string."""
    output_string = ""

    for i in input_dict:
        output_string += i.title().replace("_" or "-", " ")
        output_string += f": {input_dict[i]}{modifier} "

    return output_string


def retrieve_embed_length(embed):
    """Retrieves the character length for a given embed as an integer."""
    fields = [embed.title, embed.description, embed.footer.text,
              embed.author.name]

    fields.extend([field.name for field in embed.fields])
    fields.extend([field.value for field in embed.fields])

    total = ""
    for item in fields:
        total += str(item) if str(item) != 'Embed.Empty' else ''

    return len(total)
