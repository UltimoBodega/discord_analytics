import app_configs.config_manager as app_conf
from bodega_bot import app
from db.db import DB

#------------- Main Program -------------#
def main():
    app_conf.user_input()
    DB.get_instance().setup_db()
    app.bodega_bot()

if __name__ == '__main__':
    main()