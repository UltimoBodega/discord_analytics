from __future__ import annotations

import json
import os
import pathlib


class ConfigManager:

    __instance = None

    @staticmethod
    def get_instance() -> ConfigManager:
        """
        Gets singleton class of config manager
        @return: a config manager
        """
        if ConfigManager.__instance is None:
            ConfigManager()
        return ConfigManager.__instance


    def __init__(self):
        """
        Private singleton constructor
        """
        if ConfigManager.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            ConfigManager.__instance = self

        config_path = f'{str(pathlib.Path(__file__).parent.absolute())}/config.json'
        self.config_dict = {}
        if os.path.exists(config_path):
            print(f'Loading config file: {config_path}')
            self.config_dict = json.load(open(config_path))
        else:
            print(f'Not loading config file: {config_path} since it does not exist')


    def get_db_url(self) -> str:
        """
        @return: The configured database name or default url
        """
        return self.config_dict['db_url'] if 'db_url' in self.config_dict else 'sqlite:///bodega_discord.db'


    def get_bot_token(self) -> str:
        """
        @return: The configured bot token or default test bodega token
        """
        return self.config_dict['bot_token'] if 'bot_token' in self.config_dict else \
            'Nzk1ODk2NzQzODM2NTE2MzYy.X_QCmg.2HC3k6f-XF1Iuvcab0j3B8IjAiA'
