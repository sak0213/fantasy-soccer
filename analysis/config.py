from creds import api_key

req_headers = {
  'x-apisports-key': api_key
}

base_url = 'https://v3.football.api-sports.io/'

focus_league = 39

# Database config
local_name = "football"
local_user = "postgres"
local_host = "localhost"
local_port = "5432"