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