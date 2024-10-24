import psycopg2
from config import local_host, local_name, local_port, local_user
from creds import local_db_password
import pandas as pd
import warnings
import random
warnings.simplefilter('ignore')
conn = psycopg2.connect(dbname=local_name, user =local_user, host=local_host, password=local_db_password, port =local_port)
cur = conn.cursor()

class TeamProfile:
    def __init__(self, game_id=None, setup_parameter=None) -> None:
        """
        Creates object for a specific team's statistics.\n
        This will manage querying DB for initial lineup stats\n
        and handle any modifications due to home/away\n
        or other probablistic cirumstances.
        """
        pass

    def is_home(self) -> None:
        pass

    def init_goalie_stats(self) -> None:
        pass

    def init_passing_stats(self) -> None:
        pass

    def init_shooting_stats(self) -> None:
        pass

    def init_dribble_stats(self) -> None:
        pass

    def init_defensive_stats(self) -> None:
        pass

    def init_stats(self) -> None:
        self.init_goalie_stats()
        self.init_passing_stats()
        self.init_shooting_stats()
        self.init_dribble_stats()
        self.init_defensive_stats()

    def mod_mode(self) -> None:
        pass

class GameManager:
    def __init__(self, game_id=None, setup_json=None) -> None:
        pass

