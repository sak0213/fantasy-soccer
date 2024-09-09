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
