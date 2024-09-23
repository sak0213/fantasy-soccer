import psycopg2
from config import local_host, local_name, local_port, local_user
from creds import local_db_password
import pandas as pd
import warnings
import random
warnings.simplefilter('ignore')
conn = psycopg2.connect(dbname=local_name, user =local_user, host=local_host, password=local_db_password, port =local_port)
cur = conn.cursor()
import time

