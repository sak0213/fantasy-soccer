from sim_classes import TeamStatGen, TeamProfile, GameManager
from config import game_setup

fixture = 1035551
# fixture = 1035338

def sim(fixture:int = None, output = 'print_full'): #type: ignore

    team_stats = TeamStatGen(fixture)
    home_team = TeamProfile(team_stats.configure_team_stats('home'))
    away_team = TeamProfile(team_stats.configure_team_stats('away'))
    game = GameManager(home_team, away_team, game_setup)
    game.run_game(output)

for i in range(5):
    sim(fixture)