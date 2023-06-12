import os
import environ


class CustomEnvironment:
    env = environ.Env(
        DATABASE_PASSOWRD=(str, "postgres"),
        DATABASE_USER=(str, "postgres"),
        DATABASE_NAME=(str, "postgres"),
        INITIAL_CREDITS=(int, 10),
        ADDITION_CREDITS=(int, 10),
        CREDITS_FOR_WIN=(int, 4),
    )

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
    print(BASE_DIR)

    _secret_key = env.str("SECRET_KEY")
    _database_ip = env.str("DATABASE_IP")
    _database_password = env.str("DATABASE_PASSWORD")
    _database_user = env.str("DATABASE_USER")
    _database_name = env.str("DATABASE_NAME")
    _initial_credits = env.int("INITIAL_CREDITS")
    _addition_credits = env.int("ADDITION_CREDITS")
    _credits_for_win = env.int("CREDITS_FOR_WIN")

    @classmethod
    def get_secret_key(cls) -> str:
        return cls._secret_key

    @classmethod
    def get_database_ip(cls) -> str:
        return cls._database_ip

    @classmethod
    def get_database_password(cls) -> str:
        return cls._database_password

    @classmethod
    def get_database_user(cls) -> str:
        return cls._database_user

    @classmethod
    def get_database_name(cls) -> str:
        return cls._database_name

    @classmethod
    def get_initial_credits(cls) -> int:
        return cls._initial_credits

    @classmethod
    def get_addition_credits(cls) -> int:
        return cls._addition_credits

    @classmethod
    def get_credits_for_win(cls) -> int:
        return cls._credits_for_win
