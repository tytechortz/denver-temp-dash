import os

import psycopg2 as ps

# define credentials 
credentials = {'POSTGRES_ADDRESS' : 'env-data.cvyvifniye47.us-west-1.rds.amazonaws.com', # change to your endpoint
               'POSTGRES_PORT' : '5432', # change to your port
               'POSTGRES_USERNAME' : 'postgres', # change to your username
               'POSTGRES_PASSWORD' : 'mellowyellow77', # change to your password
               'POSTGRES_DBNAME' : 'postgres'} # change to your db name
# create connection and cursor    
conn = ps.connect(host=credentials['POSTGRES_ADDRESS'],
                  database=credentials['POSTGRES_DBNAME'],
                  user=credentials['POSTGRES_USERNAME'],
                  password=credentials['POSTGRES_PASSWORD'],
                  port=credentials['POSTGRES_PORT'])
cur = conn.cursor()

cur.execute("""SELECT * FROM denver_norms;""")
# cur.fetchall()

print(cur.fetchall())