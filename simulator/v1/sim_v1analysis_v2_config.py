# Database config
local_name = "football"
local_user = "postgres"
local_host = "localhost"
local_port = "5432"


v1_setup_json = {
    'team_home':None,
    'team_away':None,
    'minutes': 90,
    'ticks_per_minute': 15,
    'rolling_params' : {
        'keep': 0.24,
        'defence_initiation': 0.025,
        'pass': 0.695,
        'shoot':0.015,
        'dribble': 0.025
    },
    'home_advantage':0.006, #plus or minus this percent
    'mod_mode' : True,
    'shooting_accuracy_mod': -0.125, #changes performance by this amount
    'goalie_accuracy_mod': 0.275 #changes performance by this amount
	}

simulation_iterations = 2000

season = 2023

real_results_sql = f"""

select 
	fixture_id,
	max(team_id) filter (where team_id = team_home) as team_home,
	max(team_id) filter (where team_id = team_away) as team_away,
	max(goals_total) filter (where team_id = team_home) as home_goal,
	max(goals_total) filter (where team_id = team_away) as away_goal,
	max(shots_total) filter (where team_id = team_home) as home_shot,
	max(shots_total) filter (where team_id = team_away) as away_shot,
	max(passes_total) filter (where team_id = team_home) as home_passes,
	max(passes_total) filter (where team_id = team_away) as away_passes,
	max(dribbles_total) filter (where team_id = team_home) as home_dribble,
	max(dribbles_total) filter (where team_id = team_away) as away_dribble
	
from (
select
	fixture_id,
	team_id,
	sum(goals_total::int) as goals_total,
	sum(shots_total::int) as shots_total,
	sum(passes_total::int) as passes_total,
	sum(tackles_total::int) as total_tackles,
	sum(interceptions::int) as interceptions,
	sum(blocks::int) as blocks,
	sum(dribbles_attempted::int) as dribbles_total
from ffl.fixture_player_performance
where fixture_id in (select id from ffl.fixtures where season = '{season}')
group by fixture_id, team_id) a
left join ffl.fixtures as fix on fix.id = fixture_id
group by 1
"""
