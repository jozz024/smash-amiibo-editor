from bitstring import BitString
import json
import os
from amiibo import AmiiboDump
import sys

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.abspath(".")

with open(os.path.join(base_path, "resources", "personality_data.json")) as groups:
    groups_data = json.load(groups)


param_defs = [
    ("near", 7),
    ("offensive", 7),
    ("grounded", 7),
    ("attack_out_cliff", 6),
    ("dash", 7),
    ("return_to_cliff", 6),
    ("air_offensive", 6),
    ("cliffer", 6),
    ("feint_master", 7),
    ("feint_counter", 7),
    ("feint_shooter", 7),
    ("catcher", 7),
    ("_100_attacker", 6),
    ("_100_keeper", 6),
    ("attack_cancel", 6),
    ("smash_holder", 7),
    ("dash_attacker", 7),
    ("critical_hitter", 6),
    ("meteor_master", 6),
    ("shield_master", 7),
    ("just_shield_master", 6),
    ("shield_catch_master", 6),
    ("item_collector", 5),
    ("item_throw_to_target", 5),
    ("dragoon_collector", 4),
    ("smashball_collector", 4),
    ("hammer_collector", 4),
    ("special_flagger", 4),
    ("item_swinger", 5),
    ("homerun_batter", 4),
    ("club_swinger", 4),
    ("death_swinger", 4),
    ("item_shooter", 5),
    ("carrier_broker", 5),
    ("charger", 5),
    ("appeal", 5),
    # the ones below here are unused for personality calculations but still useful for the parser
    ("fighter_01", 7),
    ("fighter_02", 7),
    ("fighter_03", 7),
    ("fighter_04", 7),
    ("fighter_05", 7),
    ("advantagious_fighter", 7),
    ("weaken_fighter", 7),
    ("revenge", 7),
    ("attack_s", 10),
    ("attack_hi", 10),
    ("attack_lw", 10),
    ("smash_s", 10),
    ("smash_hi", 10),
    ("smash_lw", 10),
    ("special_n", 10),
    ("special_s", 10),
    ("special_hi", 10),
    ("special_lw", 10),
    ("attack_air_f", 9),
    ("attack_air_b", 9),
    ("attack_air_hi", 9),
    ("attack_air_lw", 9),
    ("special_air_n", 9),
    ("special_air_s", 9),
    ("special_air_hi", 9),
    ("special_air_lw", 9),
    ("escape_air_forward", 8),
    ("escape_air_backward", 8),
    ("appeal_hi", 7),
    ("appeal_lw", 7),
]


personality_names = [
    "Normal",
    # def
    "Cautious",
    "Realistic",
    "Unflappable",
    # agl
    "Light",
    "Quick",
    "Lightning Fast",
    # ofn
    "Enthusiastic",
    "Aggressive",
    "Offensive",
    # rsk
    "Reckless",
    "Thrill Seeker",
    "Daredevil",
    # gen
    "Versatile",
    "Tricky",
    "Technician",
    # ent
    "Show-Off",
    "Flashy",
    "Entertainer",
    # cau
    "Cool",
    "Logical",
    "Sly",
    # dyn
    "Laid Back",
    "Wild",
    "Lively",
]


def decode_behavior_params(dump: AmiiboDump):
    params = {}

    # This data gets a lot simpler to read if you treat it as a bitstream
    # and then read it "in reverse" (flip the bytes, then read bits back to front = no byte swap issues)
    behavior_data = dump.data[0x1BC:0x1F6]

    bits = BitString(behavior_data[::-1])
    for name, size in param_defs[::-1]:
        val = bits.read("uint:{}".format(size))

        # even the game internals work with "out of 100" values so we'll keep doing that here
        val_max = (1 << size) - 1
        params[name] = val / val_max * 100
    return params


def scale_value(param, value, flip):
    # the original code actually defines a default of 0 for "appeal", and then divides by it
    # on ARM this just results in 0, anywhere else it'll blow up ;)
    if param == "appeal":
        return 0.25

    # some of the "directional weight" parameters have different defaults defined in the code but none of them are ever used here so lol
    default = 50
    if flip:
        scaled = (default - value) / default
    else:
        scaled = (value - default) / default

    # since we rescale to range from -1.0 to 1.0, this means values below halfway are meaningless lol
    return max(0, min(1, scaled))


def calculate_group_score(params, group):
    score = 0
    for param_data in group["scores"]:
        name = param_data["param"]
        value = scale_value(name, params[name], param_data["flip"])

        if value >= param_data["min_1"]:
            score += param_data["point_1"]
        if value >= param_data["min_2"]:
            score += param_data["point_2"]

    return score


def meets_group_necessary_requirements(params, group):
    name = group["necessary_param"]
    if not name:
        return True

    value = scale_value(name, params[name], group["necessary_flip"])
    return value >= group["necessary_min"]


def get_personality_tier(group, score):
    winner = 0  # default is Normal
    for tier in group["tiers"]:
        if score >= tier["points"]:
            winner = tier["personality"]
    return winner


def calculate_personality(params):
    group_scores = []

    for group_id, group_data in groups_data.items():
        if not meets_group_necessary_requirements(params, group_data):
            continue

        score = calculate_group_score(params, group_data)

        # using numeric index as a tiebreaker here
        key = (score, group_data["index"])
        group_scores.append((key, group_data))


    if not group_scores:
        # if no groups are eligible, we're Normal
        return 0

    # find the best group!
    (winner_score, _), winner_group = max(group_scores)
    return get_personality_tier(winner_group, winner_score)

def calculate_personality_from_data(params):

    personality = calculate_personality(params)
    return personality_names[personality]