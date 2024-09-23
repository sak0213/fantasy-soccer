# Database config
local_name = "football"
local_user = "postgres"
local_host = "localhost"
local_port = "5432"


real_results_sql = f"""
select
	fixture_id,
	home_goal,
	away_goal,
	home_shot,
	away_shot,
	1 - (away_goal * 1.0/ nullif(away_shot_on,0)) as home_goalie_save_rate,
	1 - (home_goal * 1.0/ nullif(home_shot_on,0)) as away_goalie_save_rate,
	home_passes_attempt,
	away_passes_attempt,
	home_passes_success *1.0  / nullif(home_passes_attempt,0) as home_pass_accuracy,
	away_passes_success *1.0 / nullif(away_passes_attempt,0) as away_pass_accuracy,
	home_tackles,
	away_tackles,
	home_blocks *1.0 / nullif(away_shot, 0) as home_shot_blocks,
	away_blocks *1.0 / nullif(home_shot, 0) as away_shot_blocks,
	home_interceptions *1.0  / nullif(away_passes_attempt,0) as home_interception_rate,
	away_interceptions *1.0 / nullif(home_passes_attempt,0) as away_interception_rate,
	home_dribble_attempt,
	away_dribble_attempt,
	home_dribble_success *1.0 / nullif(home_dribble_attempt,0) as home_dribble_success_rate,
	away_dribble_success *1.0 / nullif(away_dribble_attempt,0) as away_dribble_success_rate	
from (	
	select 
        fixture_id,
        max(team_id) filter (where team_id = team_home) as team_home,
        max(team_id) filter (where team_id = team_away) as team_away,
        max(goals_total) filter (where team_id = team_home) as home_goal,
        max(goals_total) filter (where team_id = team_away) as away_goal,
        max(shots_total) filter (where team_id = team_home) as home_shot,
        max(shots_total) filter (where team_id = team_away) as away_shot,
		max(shots_on) filter (where team_id = team_home) as home_shot_on,
        max(shots_on) filter (where team_id = team_away) as away_shot_on,
        max(passes_total) filter (where team_id = team_home) as home_passes_attempt,
        max(passes_total) filter (where team_id = team_away) as away_passes_attempt,
        max(passes_success) filter (where team_id = team_home) as home_passes_success,
        max(passes_success) filter (where team_id = team_away) as away_passes_success,
		max(total_tackles) filter (where team_id = team_home) as home_tackles,
        max(total_tackles) filter (where team_id = team_away) as away_tackles,
		max(blocks) filter (where team_id = team_home) as home_blocks,
        max(blocks) filter (where team_id = team_away) as away_blocks,	
		max(interceptions) filter (where team_id = team_home) as home_interceptions,
        max(interceptions) filter (where team_id = team_away) as away_interceptions,
        max(dribbles_total) filter (where team_id = team_home) as home_dribble_attempt,
        max(dribbles_total) filter (where team_id = team_away) as away_dribble_attempt,
        max(dribbles_success) filter (where team_id = team_home) as home_dribble_success,
        max(dribbles_success) filter (where team_id = team_away) as away_dribble_success
    from (
    select
        fixture_id,
        team_id,
        sum(goals_total::int) as goals_total,
        sum(shots_total::int) as shots_total,
		sum(shots_on::int) as shots_on,
        sum(passes_total::int) as passes_total,
        sum(passes_accuracy::int) as passes_success,
        sum(tackles_total::int) as total_tackles,
        sum(interceptions::int) as interceptions,
        sum(blocks::int) as blocks,
        sum(dribbles_attempted::int) as dribbles_total,
        sum(dribbles_success::int) as dribbles_success
    from ffl.fixture_player_performance
    where fixture_id in (select id from ffl.fixtures where season = '2023')
    group by fixture_id, team_id) a
    left join ffl.fixtures as fix on fix.id = fixture_id
    group by 1) b
    """


fetch_player_records_sql = """
select * from ffl.fixtures_tactics as fix
left join 
(select
        team_id,
		player_id,
		sum(minutes::int) as minutes,
        sum(goals_total::int) as goals_total,
        sum(shots_total::int) as shots_total,
		sum(shots_on::int) as shots_on,
        sum(passes_total::int) as passes_total,
        sum(passes_accuracy::int) as passes_success,
        sum(tackles_total::int) as total_tackles,
        sum(interceptions::int) as interceptions,
        sum(blocks::int) as blocks,
        sum(dribbles_attempted::int) as dribbles_total,
        sum(dribbles_success::int) as dribbles_success
from ffl.fixture_player_performance
where fixture_id in (
	select 
	id
	from ffl.fixtures
	where (team_home in 
		(select
		team_home as team
		from ffl.fixtures 
		where id = 1035137
		union
		select
		team_away as team
		from ffl.fixtures 
		where id = 1035137)
	or team_away in
		(select
		team_home as team
		from ffl.fixtures 
		where id = 1035137
		union
		select
		team_away as team
		from ffl.fixtures 
		where id = 1035137))
	and (split_part(season_round, '-',2)::int < (select split_part(season_round, '-',2)::int from ffl.fixtures where id = 1035137)
		 and
		 split_part(season_round, '-',2)::int >= (select split_part(season_round, '-',2)::int - 3 from ffl.fixtures where id = 1035137))
	and season = (select season from ffl.fixtures where id = 1035137)
	)
and team_id in (
		select
		team_home as team
		from ffl.fixtures 
		where id = 1035137
		union
		select
		team_away as team
		from ffl.fixtures 
		where id = 1035137)
group by team_id, player_id) as player_data on player_data.player_id = fix.player_id
where fixture_id = 1035137
"""

