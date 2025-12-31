import configparser
import os

CURRENT = os.path.dirname(os.path.abspath(__file__))
GENERAL_CONFIG = "./config.ini"


def get_general_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join(CURRENT, GENERAL_CONFIG))

    config_dict = dict()

    config_dict["experiment_mode"] = config["DEFAULT"].getint("experiment_mode")
    config_dict["challs"] = config["DEFAULT"].getint("challs")
    config_dict["pre_quest"] = os.getenv("PRE_QUEST_URL", "")
    config_dict["post_quest"] = os.getenv("POST_QUEST_URL", "")

    return config_dict


def get_chall_config(chall_id):
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join(CURRENT, GENERAL_CONFIG))

    config_dict = dict()

    chall_section = "chall{0}".format(chall_id)
    for key in config[chall_section]:
        if key == "obfuscation":
            config_dict[key] = config[chall_section].getboolean("obfuscation")
        else:
            config_dict[key] = config[chall_section][key]

    return config_dict
