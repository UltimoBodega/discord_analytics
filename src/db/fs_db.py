import firebase_admin  # type: ignore
from firebase_admin import credentials  # type: ignore
from firebase_admin import firestore  # type: ignore
from app_configs.config_manager import ConfigManager


def init_fs_db() -> None:
    cred = credentials.Certificate(ConfigManager.get_instance().get_sa_filepath())
    firebase_admin.initialize_app(cred)


def get_fs_db() -> firebase_admin.firestore.client:
    return firestore.client()
