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

        self.config_dict = {}
        self.arg_dict = {}
        self.load_config_file(f'{str(pathlib.Path(__file__).parent.absolute())}/config.json')

    def load_config_file(self, filepath: str) -> None:
        """
        Attempts to load config file located at filepath.
        """
        if os.path.exists(filepath):
            print(f'Loading config file: {filepath}')
            self.config_dict = json.load(open(filepath))
        else:
            print(f'Not loading config file: {filepath} since it does not exist')


    def get_db_url(self) -> str:
        """
        @return: The configured database name or default url
        """
        return self.config_dict['db_url'] if 'db_url' in self.config_dict else 'sqlite:///bodega_discord.db'


    def get_bot_token(self) -> str:
        """
        @return: The configured bot token or default test bodega token
        """
        bot_token = ""
        if 'bot_token' in self.config_dict:
            if self.config_dict['bot_token']:
                bot_token = self.config_dict['bot_token']

        if 'bot_token' in self.arg_dict:
            if self.arg_dict['bot_token']:
                bot_token = self.arg_dict['bot_token']

        return bot_token

    def inject_parsed_arguments(self, arguments: dict) -> None:
        """
        Populates private argument dictionary.
        """
        for argument, value in arguments.items():
            self.arg_dict[argument] = value



