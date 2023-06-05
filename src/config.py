import os
import environ

class CustomEnvironment:
    env = environ.Env(
        DATABASE_PASSOWRD=(str, 'postgres'),
        DATABASE_USER=(str, 'postgres'),
        DATABASE_NAME=(str, 'postgres'),
    )

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    print(BASE_DIR)

    _secret_key = env.str('SECRET_KEY')
    _database_ip = env.str('DATABASE_IP')
    _database_password = env.str('DATABASE_PASSWORD')
    _database_user = env.str('DATABASE_USER')
    _database_name = env.str('DATABASE_NAME')
    

    @classmethod
    def get_secret_key(cls) -> str:
        return cls._secret_key
    
    @classmethod
    def get_database_ip(cls) -> str:
        return cls._database_ip
    
    @classmethod
    def get_database_password(cls) ->str:
        return cls._database_password
    
    @classmethod
    def get_database_user(cls) -> str:
        return cls._database_user
    
    @classmethod
    def get_database_name(cls) -> str:
        return cls._database_name
    

