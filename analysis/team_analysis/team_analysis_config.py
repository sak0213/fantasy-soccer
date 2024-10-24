# Database config
local_name = "football"
local_user = "postgres"
local_host = "localhost"
local_port = "5432"


team_results_sql = """
 select 
	team,
	season,
	sum(score_for) as score_for,
	sum(score_against) as score_against,
	sum(wins) as wins,
	sum(loss) as losses,
	sum(tie) as tie,
	sum(wins) + sum(loss) + sum(tie) as games_played,
	round(sum(score_for)^1.83 / (sum(score_for)^1.83 + sum(score_against)^1.83),2) as pythag_wl,
	round(sum(wins) * 1.0 / (sum(wins) + sum(loss)), 2) as real_wl
from (
	select
		team_home as team,
		season,
		score_home as score_for,
		score_away as score_against,
		case when
			score_home > score_away then 1
		else 0 end as wins,
			case when
			score_home < score_away then 1
		else 0 end as loss,
			case when
			score_home = score_away then 1
		else 0 end as tie
	from ffl.fixtures
	union
	select
		team_away as team,
		season,
		score_away as score_for,
		score_home as score_against,
		case when
			score_home > score_away then 1
		else 0 end as loss,
			case when
			score_home < score_away then 1
		else 0 end as win,
			case when
			score_home = score_away then 1
		else 0 end as tie
	from ffl.fixtures) a
group by team, season
"""