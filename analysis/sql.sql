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
from ffl.fixtures) foo
group by team