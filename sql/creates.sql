create schema if not exists ffl;
create schema if not exists ffl_prod;
create schema if not exists ffl_staging;

create table if not exists ffl.teams (
    id int primary key not null,
    name varchar(50) not null,
    code varchar(4)
);

create table if not exists ffl.players (
    id int primary key not null,
    current_team_id int,
    season varchar(4),
    position varchar(20),
    name_first varchar(50),
    name_last varchar(50),
    name_easy varchar(50),
    height varchar(6),
    weight varchar(6)
    date_of_birth date,
    constraint fk_player_team foreign key (current_team_id) references ffl.teams(id)
    );

create table if not exists ffl.fixtures (
    id int primary key not null,
    date date,
    season varchar(4),
    team_home int,
    constraint fk_fixture_team0 foreign key (team_home) references ffl.teams(id),
    team_away int,
    constraint fk_fixture_team1 foreign key (team_away) references ffl.teams(id),
    tracking_status varchar(15),
    referee varchar(25),
    score_home int,
    score_away int
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
    dribbles_past varchar(4),
    dribbles_success varchar(4),
    dribbles_attempted  varchar(4),
    foul_drawn varchar(4),
    foul_committed varchar(4),
    cards_yellow varchar(4),
    cards_red varchar(4),
    penalty_won varchar(4),
    penalty_committed varchar(4),
    penalty_scored varchar(4),
    penalty_missed varchar(4),
    penalty_saved varchar(4),
    duals_won varchar(4),
    duals_total varchar(4),
    constraint fk_fixture_team_players primary key (fixture_id, team_id, player_id)
);

create table if not exists ffl_staging.job_manager (
    id serial,
    time_generated timestamp not null default (now() at time zone 'utc'),
    query_scope varchar(30),
    query_params text,
    status varchar(20)
);

create table if not exists ffl_staging.query_data (
    id serial,
    job_id int,
    query_scope varchar(30),
    response_data text,
    status varchar(20)
);


create table ffl.fixtures_tactics (
    fixture_id int,
    team_id int,
    team_formation varchar(11),
    player_id int,
    position varchar(2),
    start_gric varchar(3),
    constraint fk_fixture_lineups primary key (fixture_id, team_id, player_id)
);