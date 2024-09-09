create or replace procedure ffl.fixture_player_performance()
language plpgsql
as $$ begin

insert into ffl.fixture_player_performance (
    fixture_id,
    team_id,
    player_id,
    minutes,
    rating,
    captain,
    substitute,
    offsides,
    shots_total,
    shots_on,
    goals_total,
    goals_conceded,
    assists,
    saves,
    passes_total,
    passes_key,
    passes_accuracy,
    tackles_total,
    blocks,
    interceptions,
    dribbles_past,
    dribbles_success,
    dribbles_attempted,
    foul_drawn,
    foul_committed,
    cards_yellow,
    cards_red,
    penalty_won,
    penalty_committed,
    penalty_scored,
    penalty_missed,
    penalty_saved,
    duals_won,
    duals_total
)
select 
	fixture_id,
	team_id,
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
		cast(teams -> 'team' ->> 'id' as int) as team_id,
		jsonb_array_elements(teams::jsonb->'players') players
	from (
		select 
			cast(response_data::jsonb -> 'parameters' ->> 'fixture' as int) as fixture_id,
			jsonb_array_elements(response_data::jsonb->'response') teams
		from ffl_staging.query_data
		where status = 'loaded' and query_scope = 'fixtures/players') a 
		) b
on conflict on constraint fk_fixture_team_players do nothing;

update ffl_staging.query_data
set status = 'parsed_player';


end; $$;


 begin

insert into ffl.fixtures_tactics (
	fixture_id,
	team_id,
	team_formation,
	player_id,
	position,
	start_grid)
select
	fixture_id,
	team_id,
	formation,
	cast(players -> 'player' ->> 'id' as int) player_id,
	players -> 'player' ->> 'pos' as position,
	players -> 'player' ->> 'grid' as start_grid	
from (
	select
		cast(fixture_id as int) as fixture_id,
		cast(teams -> 'team' ->> 'id' as int) as team_id,
		teams ->> 'formation' as formation,
		jsonb_array_elements(teams -> 'startXI') players
	from (
		select
			response_data::jsonb -> 'parameters' ->> 'fixture' as fixture_id,
			jsonb_array_elements(response_data::jsonb -> 'response') teams
		from ffl_staging.query_data
		where query_scope = 'fixtures/lineups' and status = 'loaded') a ) b
		
on conflict on constraint fk_fixture_lineups do nothing;

update ffl_staging.query_data
set status = 'parsed_fixturelineup';

end; 