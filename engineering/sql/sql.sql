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

----------------------
-- new player performance table
drop table ffl_prod.player_summaries;
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
	sum(passes_accuracy::int * passes_total::int) as passes_accuracy,
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
into table ffl_prod.player_summaries
from ffl.fixture_player_performance as fp
left join (select id, season from ffl.fixtures) as fix on fix.id = fp.fixture_id
group by fix.season, fp.player_id



-- new attempt at the rolling stats view
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
	sum(passes_accuracy::int * passes_total::int) as passes_accuracy,
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
-- into table ffl_prod.player_summaries
from ffl.fixture_player_performance as fp
left join (select id, season, season_round from ffl.fixtures) as fix on fix.id = fp.fixture_id
where (
	(select ((season::int * 100) + split_part(season_round, ' - ', 2)::int) from ffl.fixtures where id = 1035338) --focus game filter
	- ((season::int * 100) + split_part(fix.season_round, ' - ', 2)::int)
		) < 5 --game lookback
group by fix.season, fp.player_id
having fp.player_id in (select player_id from ffl.fixtures_tactics where fixture_id = 1035338)  --focus game filter




--analysis
select * 
from(
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
	sum(passes_accuracy::int * passes_total::int) as passes_accuracy,
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
-- into table ffl_prod.player_summaries
from ffl.fixture_player_performance as fp
left join (select id, season, season_round from ffl.fixtures) as fix on fix.id = fp.fixture_id
where (
	(select ((season::int * 100) + split_part(season_round, ' - ', 2)::int) from ffl.fixtures where id = 1035338) --focus game filter
	- ((season::int * 100) + split_part(fix.season_round, ' - ', 2)::int)
		) < 5 --game lookback
group by fix.season, fp.player_id
having fp.player_id in (select player_id from ffl.fixtures_tactics where fixture_id = 1035338)) a
left join (select player_id, team_id, position from ffl.fixtures_tactics where fixture_id = 1035338) as fix_deets on fix_deets.player_id = a.player_id

