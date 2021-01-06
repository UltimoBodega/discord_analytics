import argparse
from app_configs.config_manager import ConfigManager
from bodega_bot import app

def user_input() -> None:
    """
    Collects all the user inputs from the CLI
    """
    parser = argparse.ArgumentParser(
        description="smart-nine generates an instagram user's smart top 9 photograph collage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@')

    parser.add_argument('-bot_token', '-b', type=str, default="", help='Discord Bot token')
    parser.add_argument('--db_url', '-d', type=str, default="", help='Database url or connection string.')
    parser.add_argument('--config-path', '--config_path', '-c', type=str, default="", help='Filepath to configuration file.')
    args = parser.parse_args()
    ConfigManager.get_instance().load_config_file(args.config_path)

    if args.bot_token == "" and ConfigManager.get_instance().get_bot_token() == "":
        parser.print_help()
        raise ValueError('Must provide a Discord Bot token OR a config file containing a Bot token')
    
    ConfigManager.get_instance().inject_parsed_arguments(args.__dict__)


#------------- Main Program -------------#
def main():
    user_input()
    app.bodega_bot()

if __name__ == '__main__':
    main()