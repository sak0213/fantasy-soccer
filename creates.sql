create schema if not exists ffl;
create schema if not exists ffl_prod;
create schema if not exists ffl_staging;

create table if not exists ffl.teams (
    id int primary key not null,
    name varchar(24) not null
);

create table if not exists ffl.players (
    id int primary key not null,
    current_team_id int,
    position varchar(20),
    name_first varchar(25),
    name_last varchar(25),
    name_full varchar(50),
    name_easy varchar(25)
    constraint fk_player_team foreign key (current_team_id) references ffl.teams(id)
    );

create table if not exists ffl.fixtures (
    id int primary key not null,
    date date,
    season varchar(4),
    team_home int,
    constraint fk_fixture_team0 foreign key (team_home) references ffl.teams(id),
    team_away int,
    constraint fk_fixture_team1 foreign key (team_away) references ffl.teams(id)
);

create table if not exists ffl.fixture_player_performance (
    fixture_id int,
    constraint fk_fixtureEvent_fixture foreign key (fixture_id) references ffl.fixtures,
    team_id int,
    constraint fk_fixtureEvent_teams foreign key (team_id) references ffl.teams,
    player_id int,
    constraint fk_fixtureEvents_players foreign key (player_id) references ffl.players,
    minutes varchar(4),
    rating varchar(4),
    captain boolean,
    substitute boolean,
    offsides varchar(4),
    shots_total varchar(4),
    shots_on varchar(4),
    goals_total varchar(4),
    goals_conceded varchar(4),
    assists varchar(4),
    saves varchar(4),
    passes_total varchar(4),
    passes_key varchar(4),
    passes_accuracy varchar(4),
    tackles_total varchar(4),
    blocks varchar(4),
    interceptions varchar(4),
    duels_attempts varchar(4),
    duels_success varchar(4),
    duels_past varchar(4),
    foul_drawn varchar(4),
    foul_committed varchar(4),
    cards_yellow varchar(4),
    cards_red varchar(4),
    penalty_won varchar(4),
    penalty_committed varchar(4),
    penalty_scored varchar(4),
    penalty_missed varchar(4),
    penalty_saved varchar(4)
);