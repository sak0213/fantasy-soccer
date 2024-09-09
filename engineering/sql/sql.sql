select t.id, t.name, pythag_wl into ffl_prod.team_profiles from (
select team, sum(score_for) as score_for, sum(score_against) as score_against, sum(score_for)^1.83 / (sum(score_for)^1.83 + sum(score_against)^1.83) as pythag_wl
from (
select
	id as fid,
	team_home as team,
	score_home as score_for,
	score_away as score_against
from ffl.fixtures
union
select
	id as fid,
	team_away as team,
	score_away as score_for,
	score_home as score_against
from ffl.fixtures) a
group by team) b
left join ffl.teams as t on t.id = b.team



select 
	id,
	date,
	case when a.team_home = 40 then a.team_away else a.team_home end as team_away,
	case when a.team_home = 40 then a.score_home else a.score_away end as score_for,
	case when a.team_home = 40 then a.score_away else a.score_home end as score_against
from (
	select * from ffl.fixtures
	where season = '2023' and 
	(team_home = 40 or team_away = 40)) a;
	
	select * from ffl_prod.team_profiles where id = 42


-- fixture players flatten
select 
	fixture_id,
	cast(players -> 'player' -> 'id' as int) as player_id,
	coalesce(cast(players -> 'statistics' -> 0 -> 'games' ->> 'minutes' as int), 0) as minutes,
	coalesce(cast(players -> 'statistics' -> 0 -> 'games' ->> 'rating' as float), 0) as rating,
	cast(players -> 'statistics' -> 0 -> 'games' ->> 'captain' as bool) as captain,
	cast(players -> 'statistics' -> 0 -> 'games' ->> 'substitute' as bool) as substitute,
	coalesce(cast(players -> 'statistics' -> 0 ->> 'offsides' as int), 0) as offsides,
	coalesce(cast(players -> 'statistics' -> 0 -> 'shots' ->> 'total' as int), 0) as shots_total,
	coalesce(cast(players -> 'statistics' -> 0 -> 'shots' ->> 'on' as int), 0) as shots_on,
	coalesce(cast(players -> 'statistics' -> 0 -> 'goals' ->> 'total' as int), 0) as goals_total,
	coalesce(cast(players -> 'statistics' -> 0 -> 'goals' ->> 'conceded' as int), 0) as goals_conceded,
	coalesce(cast(players -> 'statistics' -> 0 -> 'goals' ->> 'assists' as int), 0) as assists,
	coalesce(cast(players -> 'statistics' -> 0 -> 'goals' ->> 'saves' as int), 0) as saves,
	coalesce(cast(players -> 'statistics' -> 0 -> 'passes' ->> 'total' as int), 0) as passes_total,
	coalesce(cast(players -> 'statistics' -> 0 -> 'passes' ->> 'key' as int), 0) as passes_key,
	coalesce(cast(players -> 'statistics' -> 0 -> 'passes' ->> 'accuracy' as int), 0) as passes_accuracy,
	coalesce(cast(players -> 'statistics' -> 0 -> 'tackles' ->> 'total' as int), 0) as tackles_total,
	coalesce(cast(players -> 'statistics' -> 0 -> 'tackles' ->> 'blocks' as int), 0) as blocks,
	coalesce(cast(players -> 'statistics' -> 0 -> 'tackles' ->> 'interceptions' as int), 0) as interceptions,
	coalesce(cast(players -> 'statistics' -> 0 -> 'dribbles' ->> 'past' as int), 0) as dribbles_past,
	coalesce(cast(players -> 'statistics' -> 0 -> 'dribbles' ->> 'success' as int), 0) as dribbles_success,
	coalesce(cast(players -> 'statistics' -> 0 -> 'dribbles' ->> 'attempts' as int), 0) as dribbles_attempts,
	coalesce(cast(players -> 'statistics' -> 0 -> 'fouls' ->> 'drawn' as int), 0) as fouls_drawn,
	coalesce(cast(players -> 'statistics' -> 0 -> 'fouls' ->> 'committed' as int), 0) as fouls_committed,
	coalesce(cast(players -> 'statistics' -> 0 -> 'cards' ->> 'yellow' as int), 0) as cards_yellow,
	coalesce(cast(players -> 'statistics' -> 0 -> 'cards' ->> 'red' as int), 0) as cards_red,
	coalesce(cast(players -> 'statistics' -> 0 -> 'penalty' ->> 'won' as int), 0) as penalty_won,
	coalesce(cast(players -> 'statistics' -> 0 -> 'penalty' ->> 'committed' as int), 0) as penalty_committed,
	coalesce(cast(players -> 'statistics' -> 0 -> 'penalty' ->> 'scored' as int), 0) as penalty_scored,
	coalesce(cast(players -> 'statistics' -> 0 -> 'penalty' ->> 'missed' as int), 0) as penalty_missed,
	coalesce(cast(players -> 'statistics' -> 0 -> 'penalty' ->> 'saved' as int), 0) as penalty_saved,
	coalesce(cast(players -> 'statistics' -> 0 -> 'duals' ->> 'won' as int), 0) as duals_won,
	coalesce(cast(players -> 'statistics' -> 0 -> 'duals' ->> 'total' as int), 0) as duals_total
from (
	select 
		fixture_id,
		jsonb_array_elements(teams::jsonb->'players') players
	from (
		select 
			response_data::jsonb -> 'parameters' ->> 'fixture' as fixture_id, jsonb_array_elements(response_data::jsonb->'response') teams
		from ffl_staging.query_data
		where status = 'loaded' and query_scope = 'fixtures/players') a 
		) b
