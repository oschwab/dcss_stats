#
#crawl-ref/source/job-data.h
#


jobs={
"Abyssal Knight" : "AK",
"Air Elementalist" : "AE",
"Arcane Marksman" : "AM",
"Artificer" : "Ar",
"Assassin" : "As",
"Berserker" : "Be",
"Chaos Knight" : "CK",
"Conjurer" : "Cj",
"Earth Elementalist" : "EE",
"Enchanter" : "En",
"Fighter" : "Fi",
"Fire Elementalist" : "FE",
"Gladiator" : "Gl",
"Hunter" : "Hu",
"Ice Elementalist" : "IE",
"Monk" : "Mo",
"Necromancer" : "Ne",
"Skald" : "Sk",
"Summoner" : "Su",
"Transmuter" : "Tm",
"Venom Mage" : "VM",
"Wanderer" : "Wn",
"Warper" : "Wr",
"Wizard" : "Wz",
"Death Knight" : "DK",
"Healer" : "He",
"Jester" : "Jr",
"Priest" : "Pr",
"Stalker" : "St"

}

#
# crawl-ref/source/species-data.h
#
species={
"Barachi" : "Ba",
"Centaur": "Ce",
"Deep Dwarf": "DD",
"Deep Elf": "DE",
"Demigod": "Dg",
"Draconian": "Dr",
# "Red Draconian": "Dr",
# "White Draconian": "Dr",
# "Green Draconian": "Dr",
# "Yellow Draconian": "Dr",
# "Grey Draconian": "Dr",
# "Black Draconian": "Dr",
# "Purple Draconian": "Dr",
# "Mottled Draconian": "Dr",
# "Pale Draconian": "Dr",
"Demonspawn": "Ds",
"Felid": "Fe",
"Formicid": "Fo",
"Ghoul": "Gh",
"Gargoyle": "Gr",
"Gnoll": "Gn",
"Halfling": "Ha",
"High Elf": "HE",
"Hill Orc": "HO",
"Human": "Hu",
"Kobold": "Ko",
"Merfolk": "Mf",
"Minotaur": "Mi",
"Mummy": "Mu",
"Naga": "Na",
"Ogre": "Og",
"Octopode": "Op",
"Spriggan": "Sp",
"Tengu": "Te",
"Troll": "Tr",
"Vampire": "Vp",
"Vine Stalker": "VS",
"Sludge Elf": "SE",
"Lava Orc": "LO",
"Djinni": "Dj"
}

#
# /crawl-ref/source/god-type.h
#

gods={

    "Zin",
    "Shining One",
    "Kikubaaqudgha",
    "Yredelemnul",
    "Xom",
    "Vehumet",
    "Okawaru",
    "Makhleb",
    "Sif muna",
    "Trog",
    "Nemelex Xobeh",
    "Elyvilon",
    "Lugonu",
    "Beogh",
    "Jiyva",
    "Fedhas",
    "Cheibriados",
    "Ashenzari",
    "Dithmenos",
    "Gozag",
    "Qazlal",
    "Ru",
    "Pakellas",
    "Uskayaw",
    "Hepliaklqana",
    "Wu Jian"

}


def is_specie(string):
   return (string.lower() in list((v.lower()) for v in species.values()))

def is_background(string):
   return (string.lower() in list((v.lower()) for v in jobs.values()))


def get_short_specie(string):
    return species[string]

def get_short_background(string):
    return jobs[string]

def get_long_specie(string):
    for lg_spec,spec in species.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if spec == string:
            return lg_spec

def get_long_background(string):
    for lg_back,back in jobs.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if back == string:
            return lg_back

def validate_class_background(string):
    if (len(string)==2):
        return (is_background(string) or is_specie(string))
    if (len(string)==4):
        return ( (is_background(string[:2]) or is_specie(string[:2])) and (is_background(string[2:]) or is_specie(string[2:])))



