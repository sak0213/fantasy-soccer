import psycopg2
from config import local_host, local_name, local_port, local_user
from creds import local_db_password
import pandas as pd
import warnings
import random
warnings.simplefilter('ignore')
conn = psycopg2.connect(dbname=local_name, user =local_user, host=local_host, password=local_db_password, port =local_port)
cur = conn.cursor()
import time

class TeamPredictors:
    def __init__(self, id, data=None, setup_parameter=None):
        self.source_data = data.loc[data['current_team_id'] == id]
        self.team_id = id
        self.setup_params = setup_parameter
        self.home_or_away = self.is_home()

        self.initialize_stats()
        self.mod_mode()
        self.home_advantage()
    
    def home_advantage(self):
        if self.home_advantage == 'home':
            self.goalie_save_rate = self.goalie_save_rate * (1 + self.setup_params['home_advantage'])
            self.passing_accuracy = self.passing_accuracy * (1 + self.setup_params['home_advantage'])
            self.key_pass_likelihood = self.key_pass_likelihood * (1 + self.setup_params['home_advantage'])
            self.shooting_accuracy = self.shooting_accuracy * (1 + self.setup_params['home_advantage'])
            self.dribble_success = self.dribble_success * (1 + self.setup_params['home_advantage'])

        elif self.home_advantage == 'away':
            self.goalie_save_rate = self.goalie_save_rate * (1 - self.setup_params['home_advantage'])
            self.passing_accuracy = self.passing_accuracy * (1 - self.setup_params['home_advantage'])
            self.key_pass_likelihood = self.key_pass_likelihood * (1 - self.setup_params['home_advantage'])
            self.shooting_accuracy = self.shooting_accuracy * (1 - self.setup_params['home_advantage'])
            self.dribble_success = self.dribble_success * (1 - self.setup_params['home_advantage'])

    def mod_mode(self):
        if self.setup_params['mod_mode'] == True:
            self.shooting_accuracy = self.shooting_accuracy * (1+ self.setup_params['shooting_accuracy_mod'])
            self.goalie_save_rate = self.goalie_save_rate * (1 + self.setup_params['goalie_accuracy_mod'])
        else:
            pass
    
    def is_home(self):
        if self.team_id == self.setup_params['team_home']:
            return 'home'
        elif self.team_id == self.setup_params['team_away']:
            return 'away'

    def goalie_stats(self):
        self.goalie_save_rate = float(self.source_data['save_percentage'].loc[self.source_data['position']== 'Goalkeeper'])
        self.goalie_pass_success = float(self.source_data['pass_accuracy'].loc[self.source_data['position']== 'Goalkeeper'])
        
    def passing_stats(self):
        self.passing_accuracy = float(self.source_data['pass_accuracy'].loc[self.source_data['position'] != 'Goalkeeper'].mean())
        self.key_pass_likelihood = float(self.source_data['key_pass_percentage'].loc[self.source_data['position'] != 'Goalkeeper'].mean())

    def shooting_stats(self):
        self.shooting_accuracy = float(self.source_data['shots_on_rate'].loc[self.source_data['position'] != 'Goalkeeper'].mean())

    def dribble_stats(self):
        self.dribble_success = float(self.source_data['dribble_success_rate'].loc[self.source_data['position'] != 'Goalkeeper'].mean())

    def defensive_stats(self):
        pass

    def initialize_stats(self):
        self.goalie_stats()
        self.passing_stats()
        self.shooting_stats()
        self.dribble_stats()

class GameManager:
    def __init__(self, team_home, team_away, setup):
        self.team_home = team_home.team_id
        self.team_away = team_away.team_id
        self.posessor = team_home
        self.non_pos = team_away
        self.ball_lost = None
        self.setup = setup

        self.game_log = []

    def update_log(self, type=None):
        if type == 'goal':
            self.game_log.append({
                'team' : self.posessor.team_id,
                'event_type' : 'goal'
            })
        if type == 'pass':
            self.game_log.append({
                'team' : self.posessor.team_id,
                'event_type' : 'pass'
            })
        if type == 'shot':
            self.game_log.append({
                'team' : self.posessor.team_id,
                'event_type' : 'shot'
            })
        if type == 'dribble':
            self.game_log.append({
                'team' : self.posessor.team_id,
                'event_type' : 'dribble'
            })

    def keep_ball(self):
        pass

    def posession_change(self):
        self.ball_lost = self.posessor
        self.posessor = self.non_pos
        self.non_pos = self.ball_lost

    def shoot_ball(self):
        shot_roll = random.random()

        if shot_roll <= self.posessor.shooting_accuracy:
            self.update_log('shot')
            goalie_roll = random.random()

            if goalie_roll >= self.non_pos.goalie_save_rate:
                self.update_log('goal')
                self.posession_change()
            else:
                self.posession_change()

    def pass_ball(self):
        pass_roll = random.random()

        if pass_roll <= self.posessor.passing_accuracy:
            self.update_log('pass')
            
            key_pass_roll = random.random()
            if key_pass_roll <= self.posessor.key_pass_likelihood:
                self.shoot_ball()
            else:
                pass
        else:
            self.posession_change()

    def dribble_try(self):
        dribble_roll = random.random()
        
        if dribble_roll <=self.posessor.dribble_success:
            self.update_log('dribble')
            pass
        else:
            self.posession_change()

    def spin_wheel(self, roll_params):
        keep = roll_params['keep']
        defence_init = keep + roll_params['defence_initiation']
        pass_init = defence_init + roll_params['pass']
        shoot_init = pass_init + roll_params['shoot']
        dribble_init = shoot_init + roll_params['dribble']

        dice_roll = random.random()

        if dice_roll <= keep:
            self.keep_ball()
        elif keep < dice_roll <= defence_init:
            self.posession_change()
        elif defence_init < dice_roll <= pass_init:
            self.pass_ball()
        elif pass_init < dice_roll <= shoot_init:
            self.shoot_ball()
        elif shoot_init < dice_roll:
            self.dribble_try()
    
    def log_results(self):
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
                if event['team'] == self.team_home:
                    home_goal += 1
                else:
                    away_goal += 1
            if event['event_type'] == 'shot':
                if event['team'] == self.team_home:
                    home_shot += 1
                else:
                    away_shot += 1

            if event['event_type'] == 'pass':
                if event['team'] == self.team_home:
                    home_pass += 1
                else:
                    away_pass += 1

            if event['event_type'] == 'dribble':
                if event['team'] == self.team_home:
                    home_dribble += 1
                else:
                    away_dribble += 1

        return (home_goal, away_goal, home_shot, away_shot, home_pass, away_pass, home_dribble, away_dribble)

    def initialize_game(self):
        for segment in range(self.setup['minutes'] * self.setup['ticks_per_minute']):
            self.spin_wheel(self.setup['rolling_params'])
        return self.log_results()
    def reset_game(self):

        self.game_log = []

def simulate(fixture=None, setup_params=None, iterations=None, report_type='aggregate'):
    stats_sql = f"""
        select
            player_id,
            current_team_id,
            minutes,
            position,
            coalesce(shots_total * 1.0 / nullif(minutes, 0), 0) as shots_per_minute,
            coalesce(shots_on * 1.0 / nullif(shots_total, 0), 0) as shots_on_rate,
            coalesce(goals_total * 1.0 / nullif(shots_on, 0), 0) as goals_per_shot_on,
            coalesce(dribbles_attempted *1.0 / nullif(minutes, 0), 0) as dribbles_per_minute,
            coalesce(dribbles_success *1.0 / nullif(dribbles_attempted, 0), 0) as dribble_success_rate,
            coalesce(passes_total * 1.0 / nullif(minutes, 0), 0) as passes_per_minute,
            coalesce(passes_accuracy *1.0 / nullif(passes_total, 0), 0) as pass_accuracy,
            coalesce(passes_key * 1.0 / nullif(passes_accuracy, 0), 0) as key_pass_percentage,
            coalesce(assists *1.0 / nullif(passes_key, 0), 0) as assist_rate_per_key_pass,
            coalesce((tackles_total + interceptions + blocks)*1.0 / nullif(minutes, 0), 0) as defensive_moves_per_minute,
            coalesce(foul_committed * 1.0 / nullif(minutes, 0), 0) as fouls_committed_per_minute,
            coalesce(foul_drawn * 1.0 / nullif(minutes, 0), 0) as fouls_drawn_per_minute,
            coalesce(cards_yellow *1.0 / nullif(minutes, 0), 0) as cards_yellow_per_minute,
            coalesce(cards_red *1.0 / nullif(minutes, 0), 0) as cards_red_per_minute,
            coalesce(penalty_committed * 1.0 / nullif(minutes, 0), 0) as penalties_committed_per_minute,
            coalesce(saves *1.00 / nullif(goals_conceded + saves, 0), 0) as save_percentage
        from ffl_prod.player_summaries
        where player_id in (select player_id from ffl.fixtures_tactics where fixture_id = {fixture})
    """

    fixture_info = f"""
        select team_home, team_away from ffl.fixtures where id = {fixture};
    """
    cur.execute(fixture_info)
    for row in cur.fetchall():
        team_home = row[0]
        team_away = row[1]

    setup_params['team_home'] = team_home
    setup_params['team_away'] = team_away


    df = pd.read_sql(stats_sql, conn)

    team_a = TeamPredictors(team_home, df, setup_params)
    team_b = TeamPredictors(team_away, df, setup_params)    

        
    def output_report(report_input=None):
        test = GameManager(team_a, team_b, setup_params)
        scores_df = pd.DataFrame(columns=['home_goal', 'away_goal', 'home_shot', 'away_shot', 'home_pass', 'away_pass', 'home_dribble', 'away_dribble'])
        # time_start = time.time()
        for i in range(iterations):
            scores_df.loc[len(scores_df)] = test.initialize_game()
            test.reset_game()
        # print(f'Time to complete a one sim:  {time.time() - time_start}')
        if report_input == 'aggregate':
            output = scores_df.describe().loc['mean']
            # print(f'Sim complete for {fixture}')
            return (int(fixture), team_home, team_away, round(output[0],0), round(output[1],0), output[2], output[3], output[4], output[5], output[6], output[7])

        elif report_type == 'individual':

            return scores_df

    return output_report(report_type)

    
    # scores_df = pd.DataFrame(columns=['home_goal', 'away_goal', 'home_shot', 'away_shot', 'home_pass', 'away_pass', 'home_dribble', 'away_dribble'])
    # for i in range(iterations):
    #     test = GameManager(team_a, team_b, setup_params)
    #     scores_df.loc[len(scores_df)] = test.initialize_game()

    # output = scores_df.describe().loc['50%']
    # # print(f'Sim complete for {fixture}')
    # return (int(fixture), team_home, team_away, round(output[0],0), round(output[1],0), output[2], output[3], output[4], output[5], output[6], output[7])