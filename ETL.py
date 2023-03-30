import pandas as pd
from cassandra.cluster import Cluster
import json
import uuid
import requests

'''

PARTIE EXTRACTION ET TRANSFORMATION DES DONNEES

'''

confirmed = pd.read_csv('time_series_covid19_confirmed_global.csv')
deaths = pd.read_csv('time_series_covid19_deaths_global.csv')
recovered = pd.read_csv('time_series_covid19_recovered_global.csv')

# Transformation des données

# Suppression des colonnes Lat et Long
confirmed = confirmed.drop(['Lat', 'Long', 'Province/State'], axis=1)
deaths = deaths.drop(['Lat', 'Long', 'Province/State'], axis=1)
recovered = recovered.drop(['Lat', 'Long', 'Province/State'], axis=1)

# Utilisation de la fonction melt pour regrouper les dates dans une seule colonne
df_confirmed = confirmed.melt(id_vars=['Country/Region'], var_name='Date', value_name='Nbr_cas')
df_deaths = deaths.melt(id_vars=['Country/Region'], var_name='Date', value_name='Nbr_cas')
df_recovered = recovered.melt(id_vars=['Country/Region'], var_name='Date', value_name='Nbr_cas')

# Conversion de la colonne date au format date
df_confirmed['Date'] = pd.to_datetime(df_confirmed['Date'], format='%m/%d/%y')
df_deaths['Date'] = pd.to_datetime(df_deaths['Date'], format='%m/%d/%y')
df_recovered['Date'] = pd.to_datetime(df_recovered['Date'], format='%m/%d/%y')

# Renommer colonne
df_confirmed = df_confirmed.rename(columns={'Country/Region': 'Country_region'})
df_deaths = df_deaths.rename(columns={'Country/Region': 'Country_region'})
df_recovered = df_recovered.rename(columns={'Country/Region': 'Country_region'})

# Evolution des cas par pays et date
df_agg_confirmed = df_confirmed.groupby(['Country_region', 'Date']).sum().reset_index()
df_agg_deaths = df_deaths.groupby(['Country_region', 'Date']).sum().reset_index()
df_agg_recovered = df_recovered.groupby(['Country_region', 'Date']).sum().reset_index()

# Convertir le data frame en format JSON
df_agg_confirmed.to_json('confirmed.json', orient='records')
df_agg_deaths.to_json('deaths.json', orient='records')
df_agg_recovered.to_json('recovered.json', orient='records')

'''

PARTIE CASSANDRA : Connexion, création des tables et insertion des données 

'''

# Connexion au cluster via cassandra

cluster = Cluster(['localhost'])
session = cluster.connect()

# Création de la table Cassandra
#confirmed

session.execute("CREATE KEYSPACE IF NOT EXISTS confirmed WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};")
session.execute("USE confirmed")
session.execute("""
    CREATE TABLE IF NOT EXISTS confirmed (
        id uuid PRIMARY KEY,
        Country_region text,
        Date timestamp,
        Nbr_cas int
    )
""")

# Insertion des données dans la table Cassandra
for row1 in df_confirmed.itertuples(index=False):
    date1 = row1[1].strftime("%Y-%m-%d")
    session.execute("""
        INSERT INTO confirmed (id, Country_region, Date, Nbr_cas) 
        VALUES (%s, %s, %s, %s)
    """, (uuid.uuid4(), row1[0], date1, row1[2]))

#deaths
session.execute("CREATE KEYSPACE IF NOT EXISTS deaths WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};")
session.execute("USE deaths")
session.execute("""
    CREATE TABLE IF NOT EXISTS deaths (
        id uuid PRIMARY KEY,
        Country_region text,
        Date timestamp,
        Nbr_cas int
    )
""")

# Insertion des données dans la table Cassandra
for row2 in df_deaths.itertuples(index=False):
    date2 = row2[1].strftime("%Y-%m-%d")
    session.execute("""
        INSERT INTO deaths (id, Country_region, Date, Nbr_cas) 
        VALUES (%s, %s, %s, %s)
    """, (uuid.uuid4(), row2[0], date2, row2[2]))

#recovered
session.execute("CREATE KEYSPACE IF NOT EXISTS recovered WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};")
session.execute("USE recovered")
session.execute("""
    CREATE TABLE IF NOT EXISTS recovered (
        id uuid PRIMARY KEY,
        Country_region text,
        Date timestamp,
        Nbr_cas int
    )
""")

# Insertion des données dans la table Cassandra
for row3 in df_recovered.itertuples(index=False):
    date3 = row3[1].strftime("%Y-%m-%d")
    session.execute("""
        INSERT INTO recovered (id, Country_region, Date, Nbr_cas) 
        VALUES (%s, %s, %s, %s)
    """, (uuid.uuid4(), row3[0], date3, row3[2]))


'''

 PARTIE ELASTICSEARCH : Indexation des données 

'''

# Lecture des fichiers JSON de données
with open('confirmed.json', 'r') as f:
    data_confirmed = json.load(f)

with open('deaths.json', 'r') as f:
    data_deaths = json.load(f)

with open('recovered.json', 'r') as f:
    data_recovered = json.load(f)

# Transformation des données pour Elasticsearch, un peu comme ce que jq fait

bulk_data_confirmed = ''
for item in data_confirmed:
    header = {"index": {"_index": "confirmed_cases", "_type": "confirmed", "_id": str(uuid.uuid4())}}
    bulk_data_confirmed += json.dumps(header) + '\n'
    bulk_data_confirmed += json.dumps(item) + '\n'

bulk_data_deaths = ''
for item in data_deaths:
    header = {"index": {"_index": "deaths_cases", "_type": "deaths", "_id": str(uuid.uuid4())}}
    bulk_data_deaths += json.dumps(header) + '\n'
    bulk_data_deaths += json.dumps(item) + '\n'

bulk_data_recovered = ''
for item in data_recovered:
    header = {"index": {"_index": "recovered_cases", "_type": "recovered", "_id": str(uuid.uuid4())}}
    bulk_data_recovered += json.dumps(header) + '\n'
    bulk_data_recovered += json.dumps(item) + '\n'

# Écriture des données transformées dans un fichier
with open('confirmed.evo.json', 'w') as f:
    f.write(bulk_data_confirmed)

with open('deaths.evo.json', 'w') as f:
    f.write(bulk_data_deaths)

with open('recovered.evo.json', 'w') as f:
    f.write(bulk_data_recovered)

# Paramètres de connexion à Elasticsearch

ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_USER = 'elastic'
ELASTICSEARCH_PASSWORD = 'secret'

# Index à utiliser pour l'indexation dans Elasticsearch

INDEX_CONF = 'confirmed'
INDEX_DEATHS = 'deaths'
INDEX_REC = 'recovered'

# Fonction pour envoyer les données vers Elasticsearch
def send_to_elasticsearch(index_name, data_file):
    url = f'http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}/{index_name}/_bulk'
    headers = {'Content-Type': 'application/json'}
    auth = (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    with open(data_file, 'r') as f:
        data = f.read()
    response = requests.post(url, headers=headers, auth=auth, data=data)
    if response.status_code != 200:
        print(f"Erreur lors de l'envoi des données vers Elasticsearch : {response.text}")
    else:
        print(f"Données envoyées avec succès vers l'index {index_name}.")

# Envoi des données pour chaque index à Elasticsearch

send_to_elasticsearch(f'{INDEX_CONF}/default', 'confirmed.evo.json')
send_to_elasticsearch(f'{INDEX_DEATHS}/default', 'deaths.evo.json')
send_to_elasticsearch(f'{INDEX_REC}/default', 'recovered.evo.json')
