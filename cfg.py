import configparser
import os.path

CONFIG_FILE = 'config.ini'

class Cfg:
    def __init__(self, config_file=CONFIG_FILE):
        project_dir = os.path.dirname(__file__)
        config_path = project_dir + '/' + CONFIG_FILE

        self.config = configparser.ConfigParser()

        if not self.config.read(config_path):
            raise SystemExit(f'can not find config ({config_path})')

    @property
    def database_name(self):
        return self.config['database']['name']

    @property
    def database_user(self):
        return self.config['database']['user']

    @property
    def database_password(self):
        return self.config['database']['password']

    @property
    def database_host(self):
        return self.config['database']['host']


config = Cfg()
