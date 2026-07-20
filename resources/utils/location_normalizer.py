from resources.utils import states, lgas


STATE_ALIASES = {

    "Nassarawa": "Nasarawa",

    "Federal Capital": "Federal Capital Territory",

    "Federal Capital Territory (FCT)": "Federal Capital Territory",

    "FCT": "Federal Capital Territory",

    "Abuja": "Federal Capital Territory"

}



LGA_ALIASES = {

    "Badagary": "Badagry",

    "Oturkpo": "Otukpo",

    "Katsina- Ala": "Katsina-Ala",

    "Teungo": "Toungo",

    "Kontogur": "Kontagora",

    "Abakalik": "Abakaliki",

    "Esan Centtral": "Esan Central",

    "Orhionmw": "Orhionmwon",

    "Igbo-Eti": "Igbo Etiti",

    "EnuguSou": "Enugu South",

    "AkokoNorthWest": "Akoko North-West",

    "IfeCentral": "Ife Central",

    "Qua'anpa": "Qua'an Pan",

    "Gwadabaw": "Gwadabawa",

    "Tambawal": "Tambuwal",

    "Tangazar": "Tangaza",

    "Borsari": "Bursari",

    "Koko/Bes": "Koko/Besse",

    "Dutsin-M": "Dutsin-Ma"

}




def normalize_state(state_name):
    """
    Normalize a Nigerian state name.
    """

    if not state_name:

        return None


    state_name = str(
        state_name
    ).strip()


    state_name = STATE_ALIASES.get(
        state_name,
        state_name
    )


    for state in states:

        if state.lower() == state_name.lower():

            return state


    return state_name.title()





def normalize_lga(state_name, lga_name=None):
    """
    Normalize an LGA name.
    """

    if lga_name is None:

        lga_name = state_name


    if not lga_name:

        return None


    state_name = normalize_state(
        state_name
    )


    lga_name = str(
        lga_name
    ).strip()


    lga_name = LGA_ALIASES.get(
        lga_name,
        lga_name
    )


    if state_name and state_name in lgas:

        for lga in lgas[state_name]:

            if lga.lower() == lga_name.lower():

                return lga


    return lga_name.title()





def state_exists(state_name):
    """
    Check whether a state exists.
    """

    state_name = normalize_state(
        state_name
    )


    return state_name in states





def lga_exists(state_name, lga_name):
    """
    Check whether an LGA belongs
    to a selected state.
    """


    state_name = normalize_state(
        state_name
    )


    lga_name = normalize_lga(
        state_name,
        lga_name
    )


    if state_name not in lgas:

        return False


    valid_lgas = lgas[state_name]


    return any(

        lga.lower() == lga_name.lower()

        for lga in valid_lgas

    )