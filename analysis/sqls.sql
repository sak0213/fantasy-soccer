select * from ffl.fixtures_tactics where fixture_id = 1035107 and team_id = 50;
select 
	minutes, 
	shots_total, 
	shots_on, 
	assists, 
	passes_accuracy,
	passes_total
from ffl.fixture_player_performance where fixture_id = 1035107 and team_id = 50 and player_id = 1100;

select 
player_id, 
avg(coalesce(rating::double precision, 0))
from ffl.fixture_player_performance
where fixture_id in (select fixture_id from ffl.fixtures_tactics)
group by player_id

drop table ffl_prod.player_summaries_2023;
select 
	player_id,
	play.position,
	fix.team_id,
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
	sum(passes_accuracy::int) as passes_accuracy,
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
	-- into table ffl_prod.player_summaries_2023
from ffl.fixture_player_performance as fix
left join
		(select id, position, current_team_id from ffl.players) as play on play.id = fix.player_id
group by fix.player_id, play.position, fix.team_id
having sum(minutes::int) > 0


select
	player_id,
	current_team_id,
	minutes,
	coalesce((goals_total+assists) *1.0 / nullif(minutes,0), 0) as points_per_minute,
	coalesce(shots_total * 1.0 / nullif(minutes, 0), 0) as shots_per_minute,
	coalesce(shots_on * 1.0 / nullif(shots_total, 0), 0) as shots_on_rate,
	coalesce(goals_total * 1.0 / nullif(shots_on, 0), 0) as goals_per_shot_on,
	coalesce(dribbles_attempted *1.0 / nullif(minutes, 0), 0) as dribbles_per_minute,
	coalesce(dribbles_success / nullif(dribbles_attempted, 0), 0) as dribble_success_rate,
	coalesce(passes_total * 1.0 / nullif(minutes, 0), 0) as passes_per_minute,
	coalesce(passes_accuracy *1.0 / nullif(passes_total, 0), 0) as pass_accuracy,
	coalesce(passes_key * 1.0 / nullif(passes_accuracy, 0), 0) as key_pass_percentage,
	coalesce(assists *1.0 / nullif(passes_key, 0), 0) as assist_rate_per_key_pass,
	coalesce((tackles_total + interceptions + blocks)*1.0 / nullif(minutes, 0), 0) as defensive_moves_per_minute,
	coalesce(foul_committed * 1.0 / nullif(minutes, 0), 0) as fouls_committed_per_minute,
	coalesce(foul_drawn * 1.0 / nullif(minutes, 0), 0) as fouls_drawn_per_minute,
	coalesce(cards_yellow *1.0 / nullif(minutes, 0), 0) as cards_yellow_per_minute,
	coalesce(cards_red *1.0 / nullif(minutes, 0), 0) as cards_red_per_minute,
	coalesce(penalty_committed * 1.0 / nullif(minutes, 0), 0) as penalties_committed_per_minute
from ffl_prod.player_summaries
where position != 'Defender'




-- weird player team id fix
update ffl.players
set current_team_id = team_id
from (
select player_id, team_id from(
select player_id, team_id from ffl.fixture_player_performance
group by 1,2 ) a
left join ffl.players as play on play.id = a.player_id
where team_id != current_team_id) a
where a.player_id = id

-- simulator result comparison

select 
	fixture_id,
	max(team_id) filter (where team_id = team_home) as team_home,
	max(team_id) filter (where team_id = team_away) as team_away,
	max(goals_total) filter (where team_id = team_home) as home_goals,
	max(goals_total) filter (where team_id = team_away) as away_goals,
	max(shots_total) filter (where team_id = team_home) as home_shots,
	max(shots_total) filter (where team_id = team_away) as away_shots,
	max(passes_total) filter (where team_id = team_home) as home_passes,
	max(passes_total) filter (where team_id = team_away) as away_passes,
	max(dribbles_total) filter (where team_id = team_home) as home_dribbles,
	max(dribbles_total) filter (where team_id = team_away) as away_dribbles
	
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
group by fixture_id, team_id) a
left join ffl.fixtures as fix on fix.id = fixture_id
group by 1
having fixture_id = 1035370



-------------------
-- base aggregate code
select 
	fp.fixture_id,
	fix.season,
	sum(minutes) as minutes,
	sum(shots_total) as shots_total,
	sum(shots_on) as shots_on,
	sum(goals_total) as goals_total,
	sum(goals_conceded) as goals_conceded,
	sum(assists) as assists,
	sum(saves) as saves,
	sum(passes_total) as passes_total,
	sum(passes_key) as passes_key,
	sum(passes_accuracy * passes_total) as passes_success,
	sum(tackles_total) as tackles,
	sum(blocks) as blocks,
	sum(interceptions) as interceptions,
	sum(dribbles_past) as dribbles_past,
	sum(dribbles_success) as dribbles_success,
	sum(dribbles_attempted) as dribbles_attempted,
	sum(foul_drawn) as fouls_drawn,
	sum(foul_committed) as fouls_committed,
	sum(cards_yellow) as cards_yellow,
	sum(cards_red) as cards_red,
	sum(penalty_won) as penalty_won,
	sum(penalty_committed) as penalty_committed,
	sum(penalty_scored) as penalty_scored,
	sum(penalty_saved) as penalty_saved,
	sum(duals_won) as duals_won,
	sum(duals_total) as duals_total
from ffl.fixture_player_performance as fp
left join (select id, season from ffl.fixtures) as fix on fix.id = fp.fixture_id
group by fp.fixture_id, fix.season

