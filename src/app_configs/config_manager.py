from __future__ import annotations

import json
import os
import pathlib
import argparse


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
        assert ConfigManager.__instance
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

    def _load_config_file(self, filepath: str) -> None:
        """
        Attempts to load config file located at filepath.
        """
        if os.path.exists(filepath):
            print(f'Loading config file: {filepath}')
            self.config_dict = json.load(open(filepath))
        else:
            if filepath:
                print(f'Not loading config file: {filepath} since it does not exist')

    def get_db_url(self) -> str:
        """
        @return: The configured database name or default url
        """
        return self.config_dict['db_url'] or 'sqlite:///bodega_discord.db'

    def get_bot_token(self) -> str:
        """
        @return: The configured bot token or default test bodega token
        """
        return self.config_dict['bot_token'] or ""

    def get_giphy_api_key(self) -> str:
        """
        @return: The configured Giphy API key or empty string.
        """
        return self.config_dict['giphy_key'] or ""

    def get_guild_ids(self) -> list:
        """
        @return: The Guild IDs in which to allow slash commands.
        """
        return self.config_dict['guild_ids'] or []

    def inject_parsed_arguments(self, arguments: dict) -> None:
        """
        Populates private argument dictionary.
        """
        config_path = arguments["config_path"]
        if not config_path:
            config_path = f'{str(pathlib.Path(__file__).parent.absolute())}/config.json'
        self._load_config_file(config_path)
        for argument, value in arguments.items():
            if argument not in self.config_dict:
                self.config_dict[argument] = value


def user_input() -> None:
    """
    Collects all the user inputs from the CLI
    """
    parser = argparse.ArgumentParser(
        description="smart-nine generates an instagram "
                    "user's smart top 9 photograph collage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@')

    parser.add_argument('-bot_token',
                        '-b',
                        type=str,
                        default="",
                        help='Discord Bot token')
    parser.add_argument('--db_url',
                        '-d',
                        type=str, default="",
                        help='Database url or connection string.')
    parser.add_argument('--guild_ids',
                        '--guild-ids',
                        '-gid',
                        type=list,
                        default=[],
                        help="Guild IDs in which to use slash commands.")
    parser.add_argument('--config-path',
                        '--config_path',
                        '-c',
                        type=str,
                        default="",
                        help='Filepath to configuration file.')
    parser.add_argument('--giphy-key',
                        '--giphy_key',
                        '-gk',
                        type=str,
                        default="",
                        help="Giphy API Key.")
    args = parser.parse_args()
    ConfigManager.get_instance().inject_parsed_arguments(args.__dict__)

    if ConfigManager.get_instance().get_bot_token() == "":
        parser.print_help()
        raise ValueError('Must provide a Discord Bot token OR a config file containing a Bot token')
