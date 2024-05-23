import os

from dotenv import load_dotenv


# стандартные настройки, что бы брать данные для бд из файла .env
class Settings():
    def __init__(self):
        load_dotenv()

        self.DB_HOST = os.environ.get("DB_HOST")
        self.DB_PORT = os.environ.get("DB_PORT")
        self.DB_NAME = os.environ.get("DB_NAME")
        self.DB_USER = os.environ.get("DB_USER")
        self.DB_PASS = os.environ.get("DB_PASS")

        self.DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
        self.DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
        self.DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
        self.DB_USER_TEST = os.environ.get("DB_USER_TEST")
        self.DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def DATABASE_URL_TEST(self):
        return f"postgresql+asyncpg://{self.DB_USER_TEST}:{self.DB_PASS_TEST}@{self.DB_HOST_TEST}:{self.DB_PORT_TEST}/{self.DB_NAME_TEST}"


settings = Settings()
