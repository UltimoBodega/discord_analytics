from db.db import DB


def test_db_connect_success() -> None:
    DB.get_instance().setup_db('sqlite://')
    DB.get_instance()


def test_db_connect_fail() -> None:
    try:
        DB.get_instance().setup_db('/fake_db.db')
        DB.get_instance()
        raise Exception('DB instance creation should have failed')
    except Exception as error_msg:
        assert str(error_msg) == "Could not parse rfc1738 URL from string '/fake_db.db'"
