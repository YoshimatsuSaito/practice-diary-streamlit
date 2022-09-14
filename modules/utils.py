import configparser


def read_config(config_path):
    """
    config情報を読み込む関数
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    config_dict = dict()
    for sector in config.keys():
        dict_sector = config[sector]
        for k, v in dict_sector.items():
            config_dict[k] = v
    return config_dict
