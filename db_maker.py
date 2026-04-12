import requests

DB_URL = "http://localhost:8000/api"


def add_editions():
    editions = [
        {"name": "Spyro's Adventures", "release_date": "2011-10-12"},
        {"name": "Giants", "release_date": "2012-10-17"},
        {"name": "Trap Team", "release_date": "2014-10-05"},
        {"name": "Swap Force", "release_date": "2013-10-13"},
        {"name": "Super Chargers", "release_date": "2015-09-20"},
        {"name": "Imaginators", "release_date": "2016-10-13"},
    ]
    for edition in editions:
        res = requests.post(DB_URL + "/editions/", json=edition)
        print(res.text)


def add_elements():
    element_names = ["Magic", "Earth", "Water", "Fire", "Tech", "Undead", "Air", "Life"]
    for element_name in element_names:
        res = requests.post(DB_URL + "/elements/", json={"name": element_name})
        print(res.text)


def add_types():
    type_names = [
        "Skylander",
        "Giant",
        "Traptanium Crystal Trap",
        "Swapper",
        "Vehicle",
        "Sensei",
        "Villain Sensei",
    ]
    for type_name in type_names:
        res = requests.post(DB_URL + "/types/", json={"name": type_name})
        print(res.text)


def add_skylanders():
    skylanders = [
        {"name": "Bash", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Bash.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Boomer", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Boomer.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Camo", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Camo.png", "element_id": 8, "variant_id": 1, "swapper": False},
        {"name": "Chop Chop", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/ChopChop.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Cynder", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Cynder.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Dino-rang", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Dino-rang.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Double Trouble", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/DoubleTrouble.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Drill Sergeant", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/DrillSergeant.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Drobot", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Drobot.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Eruptor", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Eruptor.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Flameslinger", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Flameslinger.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Ghost Roaster", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/GhostRoaster.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Gill Grunt", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/GillGrunt.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Hex", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Hex.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Ignitor", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Ignitor.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Lightning Rod", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/LightningRod.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Prism Break", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/PrismBreak.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Slam Bam", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/SlamBam.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Sonic Boom", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/SonicBoom.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Spyro", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Spyro.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Stealth Elf", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/StealthElf.png", "element_id": 8, "variant_id": 1, "swapper": False},
        {"name": "Stump Smash", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/StumpSmash.png", "element_id": 8, "variant_id": 1, "swapper": False},
        {"name": "Sunburn", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Sunburn.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Terrafin", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Terrafin.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Trigger Happy", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/TriggerHappy.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Voodood", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Voodood.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Warnado", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Warnado.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Wham-Shell", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Wham-Shell.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Whirlwind", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Whirlwind.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Wrecking Ball", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/WreckingBall.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Zap", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Zap.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Zook", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Zook.png", "element_id": 8, "variant_id": 1, "swapper": False},
    ]
    for skylander in skylanders:
        res = requests.post(DB_URL + "/items/", json=skylander)
        print(res.text)


if __name__ == "__main__":
    add_editions()
    add_elements()
    add_types()
    add_skylanders()
