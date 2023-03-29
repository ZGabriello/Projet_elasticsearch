import uuid
import pandas as pd
from cassandra.cluster import Cluster

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

