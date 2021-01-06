import app_configs.config_manager as app_conf
from bodega_bot import app

#------------- Main Program -------------#
def main():
    app_conf.user_input()
    app.bodega_bot()

if __name__ == '__main__':
    main()