import json
from base64 import b64encode

import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import os, uuid

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
df_confirmed['date'] = pd.to_datetime(df_confirmed['Date'], format='%m/%d/%y')
df_deaths['date'] = pd.to_datetime(df_deaths['Date'], format='%m/%d/%y')
df_recovered['date'] = pd.to_datetime(df_recovered['Date'], format='%m/%d/%y')

# Ajouter une colonne "type" pour garder l'information sur le type de cas
df_confirmed['Type'] = 'confirmed'
df_deaths['Type'] = 'deaths'
df_recovered['Type'] = 'recovered'

# Concaténer les dataframes en un seul dataframe
df = pd.concat([df_confirmed, df_deaths, df_recovered], axis=0, ignore_index=True)

# Réorganiser les colonnes
df = df[['Type', 'Country/Region', 'Date', 'Nbr_cas']]

# Renommer colonne
df = df.rename(columns={'Country/Region': 'Country_region'})

# Grouper les données par pays, date et type et faire la somme des cas
df_agg = df.groupby(['Country_region', 'Date', 'Type']).sum().reset_index()

print(df_agg)

# Convertir le data frame en format JSON
json_data = df_agg.to_json(orient='records')

# Écrire le JSON dans un fichier
with open('data.json', 'w') as f:
    f.write(json_data)

print(df_agg)


# lancer le container elasticsearch
# sudo docker run -d --rm -p 9200:9200 -p 9300:9300 -e "http.max_content_length= 1g" -e "discovery.type=single-node" -e "transport.host=127.0.0.1" -e ELASTIC_PASSWORD=secret --name elastic docker.elastic.co/elasticsearch/elasticsearch-platinum:6.0.0 && sleep 20

#lancer le container kibana
# sudo docker run -d --rm --link elastic:elastic-url -e "ELASTICSEARCH_URL=http://elastic-url:9200" -e ELASTICSEARCH_PASSWORD="secret" -p 5601:5601 --name kibana docker.elastic.co/kibana/kibana:6.0.0 && sleep 20

#utiliser jq pour sérialiser le json obtenu grâce à python
# cat data.json | jq -c '.[] | {"index": {"_index": "covids", "_type": "covid", "_id": .id}}, .' > data.evo.json

#indexation des données grâce à curl
# curl -s -H "Content-Type: application/json" -XPOST "http://localhost:9200/covids/default/_bulk?pretty" -u 'elastic:secret' --data-binary @data.evo.json

#il faut maintenant tout passer à cassandra 