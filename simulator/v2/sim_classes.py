import psycopg2
from config import local_host, local_name, local_port, local_user
from creds import local_db_password
import pandas as pd
import warnings
import random
warnings.simplefilter('ignore')
conn = psycopg2.connect(dbname=local_name, user =local_user, host=local_host, password=local_db_password, port =local_port)
cur = conn.cursor()

class TeamStatGen:
    def __init__(self, fixture_id: int, game_lookback:int =5, connection=conn) -> pd.DataFrame: # type: ignore
        self.fixture_id = fixture_id
        self.game_lookback = game_lookback
        self.connection = connection

        self.core_stats = self.fetch_team_stats()
        self.fetch_home_away()

    def fetch_team_stats(self) -> pd.DataFrame: #type: ignore
        team_stats_sql = f"""
            select 
                lineup.team_id,
                cast(coalesce(sum(shots_total) * 1.0 / nullif(sum(minutes), 0), 0) as double precision) as shots_per_minute,
                cast(coalesce(sum(shots_on) * 1.0 / nullif(sum(shots_total), 0), 0) as double precision) as shots_on_rate,
                cast(coalesce(sum(dribbles_attempted) *1.0 / nullif(sum(minutes), 0), 0) as double precision) as dribbles_per_minute,
                cast(coalesce(sum(dribbles_success) *1.0 / nullif(sum(dribbles_attempted), 0), 0) as double precision) as dribble_success_rate,
                cast(coalesce(sum(passes_total) * 1.0 / nullif(sum(minutes), 0), 0) as double precision) as passes_per_minute,
                cast(coalesce(sum(passes_accuracy) *1.0 / nullif(sum(passes_total), 0), 0) as double precision) as pass_accuracy,
                cast(coalesce(sum(passes_key) * 1.0 / nullif(sum(passes_accuracy), 0), 0) as double precision) as key_pass_percentage,
                cast(coalesce((sum(tackles_total) + sum(interceptions))*1.0 / nullif(sum(minutes), 0), 0) as double precision) as defensive_moves_per_minute,
                cast(coalesce(sum(foul_committed) * 1.0 / nullif(sum(minutes), 0), 0) as double precision) as fouls_committed_per_minute,
                cast(coalesce(sum(foul_drawn) * 1.0 / nullif(sum(minutes), 0), 0) as double precision) as fouls_drawn_per_minute,
                cast(coalesce(sum(cards_yellow) *1.0 / nullif(sum(minutes), 0), 0) as double precision) as cards_yellow_per_minute,
                cast(coalesce(sum(cards_red) *1.0 / nullif(sum(minutes), 0), 0) as double precision) as cards_red_per_minute,
                cast(coalesce(sum(penalty_committed) * 1.0 / nullif(sum(minutes), 0), 0) as double precision) as penalties_committed_per_minute,
                cast(coalesce(sum(saves) *1.00 / nullif(sum(goals_conceded) + sum(saves), 0), 0) as double precision) as save_percentage,
                cast(coalesce((sum(saves) + sum(blocks)) *1.00 / nullif(sum(goals_conceded) + sum(saves) + sum(blocks), 0), 0) as double precision) as shot_stop_percentage
            from ffl.fixtures_tactics as lineup
                left join (
                    select 
                        fix.season as season,
                        fp.player_id as player_id,
                        sum(minutes::int) as minutes,
                        avg(rating::double precision) as rating,
                        sum(offsides::int) as offsides,
                        sum(shots_total::int) as shots_total,
                        sum(shots_on::int) as shots_on,
                        sum(goals_total::int) as goals_total,
                        sum(goals_conceded::int) as goals_conceded,
                        sum(assists::int) as assists,
                        sum(saves::int) as saves,
                        sum(passes_total::int) as passes_total,
                        sum(passes_key::int) as passes_key,
                        coalesce(sum(passes_accuracy * 100),0) as passes_accuracy,
                        sum(tackles_total::int) as tackles_total,
                        sum(blocks::int) as blocks,
                        sum(interceptions::int) as interceptions,
                        sum(dribbles_past::int) as dribbles_past,
                        sum(dribbles_success::int) as dribbles_success,
                        sum(dribbles_attempted::int) as dribbles_attempted,
                        sum(foul_drawn::int) as foul_drawn,
                        sum(foul_committed::int) as foul_committed,
                        sum(cards_yellow::int) as cards_yellow,
                        sum(cards_red::int) as cards_red,
                        sum(penalty_won::int) as penalty_won,
                        sum(penalty_committed::int) as penalty_committed,
                        sum(penalty_scored::int) as penalty_scores,
                        sum(penalty_missed::int) as penalty_missed,
                        sum(penalty_saved::int) as penalty_saved
                    from ffl.fixture_player_performance as fp
                    left join (select id, season, season_round from ffl.fixtures) as fix on fix.id = fp.fixture_id
                    where (
                        (select ((season::int * 100) + split_part(season_round, ' - ', 2)::int) from ffl.fixtures where id = {self.fixture_id}) --focus game filter
                        - ((season::int * 100) + split_part(fix.season_round, ' - ', 2)::int)
                            ) between 1 and {self.game_lookback} --game lookback
                    group by fix.season, fp.player_id)	
                as pd on pd.player_id = lineup.player_id
            where lineup.fixture_id = {self.fixture_id} and lineup.start_grid != '0:0'
            group by lineup.team_id
        """
        return pd.read_sql(sql=team_stats_sql, con=self.connection) # type: ignore
    
    def fetch_home_away(self) -> None:
        fixture_home_away_sql = f"""
            select
                team_home,
                team_away
            from ffl.fixtures
            where id = {self.fixture_id}
        """
        cur.execute(fixture_home_away_sql)
        for i in cur.fetchall():
            self.team_home = i[0]
            self.team_away = i[1]

    def configure_team_stats(self, home_away: str =None): #type: ignore
        if home_away == 'home':
            output_df = self.core_stats.loc[self.core_stats['team_id']==self.team_home]
        elif home_away == 'away':
            output_df = self.core_stats.loc[self.core_stats['team_id']==self.team_away]
        team_config = {
            'home/away':home_away,
            'event_frequency': {
                'shots':output_df['shots_per_minute'].values[0],
                'dribbles':output_df['dribbles_per_minute'].values[0],
                'passes': output_df['passes_per_minute'].values[0],
                'defensive_move': output_df['defensive_moves_per_minute'].values[0]
            },
            'success_rates': {
                'shot_on_goal':output_df['shots_on_rate'].values[0],
                'dribble_success_rate':output_df['dribble_success_rate'].values[0],
                'pass_success':output_df['pass_accuracy'].values[0],
                'key_pass_rate':output_df['key_pass_percentage'].values[0],
                'save_percentage':output_df['save_percentage'].values[0],
                'shot_stop_percentage':output_df['shot_stop_percentage'].values[0]
            }
        }

        return team_config


class TeamProfile:
    def __init__(self, team_data:dict= None) -> None: # type: ignore
        """
        Creates object for a specific team's statistics.\n
        This will manage querying DB for initial lineup stats\n
        and handle any modifications due to home/away\n
        or other probablistic cirumstances.
        """
        self.team_config = team_data
        self.home_or_away = self.is_home()
        self.init_stats()

    def is_home(self) -> str:
        if self.team_config['home/away'] == 'home':
            return 'home'
        else:
            return 'away'

    def init_goalie_stats(self) -> None:
        self.goalie_save_rate = self.team_config['success_rates']['save_percentage']
        self.shot_stop_rate = self.team_config['success_rates']['shot_stop_percentage']

    def init_passing_stats(self) -> None:
        self.passing_accuracy= self.team_config['success_rates']['pass_success']
        self.key_pass_rate= self.team_config['success_rates']['key_pass_rate']

    def init_shooting_stats(self) -> None:
        self.shooting_accuracy = self.team_config['success_rates']['shot_on_goal']

    def init_dribble_stats(self) -> None:
        self.dribble_success = self.team_config['success_rates']['dribble_success_rate']

    def init_defensive_stats(self) -> None:
        self.defensive_move_likelhood = self.team_config['event_frequency']['defensive_move']

    def init_stats(self) -> None:
        self.init_goalie_stats()
        self.init_passing_stats()
        self.init_shooting_stats()
        self.init_dribble_stats()
        self.init_defensive_stats()

    def home_advantage(self) -> None:
        pass

    def mod_mode(self) -> None:
        pass

class GameManager:
    def __init__(self, team_home: TeamProfile, team_away: TeamProfile, setup_json:dict) -> None:
        """
        Creates game object. This will recieve a game ID, two teams,\n
        and a config json to simulate a fixture. Outputs game log.
        
        """
        self.home_team = team_home
        self.away_team = team_away
        self.homeadv_shooting = 0
        self.homeadv_passing = 0
        self.default_frequencies = {
            'keep': 0.24,
            'defence_initiation': 0.025,
            'pass': 0.695,
            'shoot':0.015,
            'dribble': 0.025
        }

        self.apply_mod_mode()
        self.initialize_posession()
        self.event_frequencies = self.generate_team_event_frequencies()
        self.apply_home_advantage()
        self.game_log = []
        self.game_ticks = setup_json['minutes'] * setup_json['ticks_per_minute']

    def initialize_posession(self) -> None:
        self.has_posession = 'home'
        self.no_posession = 'away'
        self.posessor = self.home_team
        self.non_pos = self.away_team

    def apply_home_advantage(self) -> None:
        self.homeadv_shooting = 2.1000000000000005 / 90
        self.homeadv_passing = 30.894736842105214 / 90
        
        self.home_baseline += (self.homeadv_shooting + self.homeadv_passing)
        if self.home_baseline >= 1:
            self.event_frequencies['home'] = self.default_frequencies
        else:
            self.event_frequencies['home'] = {
                'keep': 1 - self.home_baseline,
                'defence_initiation': self.away_team.team_config['event_frequency']['defensive_move'],
                'pass': self.home_team.team_config['event_frequency']['passes'] + self.homeadv_passing,
                'shoot': self.home_team.team_config['event_frequency']['shots'] + self.homeadv_shooting,
                'dribble': self.home_team.team_config['event_frequency']['dribbles']
            }

    def apply_mod_mode(self) -> None:
        #modify select attributes for both teams per setup file
        pass

    def generate_team_event_frequencies(self) -> dict:
        frequencies = {}

        self.home_baseline = self.home_team.team_config['event_frequency']['shots'] + self.home_team.team_config['event_frequency']['dribbles'] + self.home_team.team_config['event_frequency']['passes'] +self.away_team.team_config['event_frequency']['defensive_move'] + self.homeadv_shooting + self.homeadv_passing
        self.away_baseline = self.away_team.team_config['event_frequency']['shots'] + self.away_team.team_config['event_frequency']['dribbles'] + self.away_team.team_config['event_frequency']['passes'] +self.home_team.team_config['event_frequency']['defensive_move']
        
        if self.home_baseline >= 1:
            frequencies['home'] = self.default_frequencies
        else:
            frequencies['home'] = {
                'keep': 1 - self.home_baseline,
                'defence_initiation': self.away_team.team_config['event_frequency']['defensive_move'],
                'pass': self.home_team.team_config['event_frequency']['passes'],
                'shoot': self.home_team.team_config['event_frequency']['shots'],
                'dribble': self.home_team.team_config['event_frequency']['dribbles']
            }
        
        if self.away_baseline >= 1:
            frequencies['away'] = self.default_frequencies
        else:
            frequencies['away'] = {
                'keep': 1 - self.away_baseline,
                'defence_initiation': self.home_team.team_config['event_frequency']['defensive_move'],
                'pass': self.away_team.team_config['event_frequency']['passes'],
                'shoot': self.away_team.team_config['event_frequency']['shots'],
                'dribble': self.away_team.team_config['event_frequency']['dribbles']
            }
        return frequencies

    def roll_keep(self) -> None:
        pass

    def roll_shoot(self) -> None:
        shot_roll = random.random()
        rebound_rate = 0.5

        self.log_event('shot')
        if shot_roll <=self.posessor.shooting_accuracy:
            goalie_roll = random.random()
            if goalie_roll >= self.non_pos.goalie_save_rate:
                self.log_event('goal')
                self.posession_loss()
            else:
                rebound_roll = random.random()

                if rebound_roll <= rebound_rate:
                    pass
                else:
                    self.posession_loss()


    def roll_pass(self) -> None:
        pass_roll = random.random()

        if pass_roll <= self.posessor.passing_accuracy:
            self.log_event('pass')
            key_pass_roll = random.random()

            if key_pass_roll <= self.posessor.key_pass_rate:
                self.roll_shoot()
            else:
                pass
        else:
            self.posession_loss()

    def roll_dribble(self) -> None:
        dribble_roll = random.random()

        if dribble_roll <= self.posessor.dribble_success:
            self.log_event('dribble')
            pass
        else:
            self.posession_loss()

    def posession_loss(self) -> None:
        intermediary = self.has_posession
        intermed_obj = self.posessor
        self.has_posession = self.no_posession
        self.no_posession = intermediary
        self.posessor = self.non_pos
        self.non_pos = intermed_obj
        # print(f'pos_change{self.posessor.home_or_away}')

    def roll_actions(self) -> None:
        posessor_rolls = self.event_frequencies[self.has_posession]
        keep = posessor_rolls['keep']
        defence_intervention = keep + posessor_rolls['defence_initiation']
        pass_attempt = defence_intervention + posessor_rolls['pass']
        shoot = pass_attempt + posessor_rolls['shoot']
        dribble = shoot + posessor_rolls['dribble']

        roll = random.random()

        if roll <= keep:
            self.roll_keep()
        elif keep < roll <= defence_intervention:
            self.posession_loss()
        elif defence_intervention < roll <= pass_attempt:
            self.roll_pass()
        elif pass_attempt < roll <= shoot:
            self.roll_shoot()
        elif shoot < roll:
            self.roll_dribble()


    def log_event(self, event: str) -> None:
        self.game_log.append({
            'event_type':event,
            'team': self.has_posession})

    def generate_game_report(self) -> tuple:
        home_goal  = 0
        home_pass = 0
        home_shot = 0
        home_dribble = 0
        away_goal = 0
        away_shot = 0
        away_pass = 0
        away_dribble = 0
        for event in self.game_log:
            if event['event_type'] == 'goal':
                if event['team'] == 'home':
                    home_goal += 1
                else:
                    away_goal += 1
            if event['event_type'] == 'shot':
                if event['team'] == 'home':
                    home_shot += 1
                else:
                    away_shot += 1

            if event['event_type'] == 'pass':
                if event['team'] == 'home':
                    home_pass += 1
                else:
                    away_pass += 1

            if event['event_type'] == 'dribble':
                if event['team'] == 'home':
                    home_dribble += 1
                else:
                    away_dribble += 1

        return (home_goal, away_goal, home_shot, away_shot, home_pass, away_pass, home_dribble, away_dribble)

    def run_game(self, output:str = 'print_full'):
        for tick in range(self.game_ticks):
            self.roll_actions()

        if output == 'print_full':
            return self.generate_game_report()

        elif output == 'scores':
            game_results = self.generate_game_report()
            return game_results[0], game_results[1]
            # print(game_results)
        

