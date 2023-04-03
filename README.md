# Projet_elasticsearch

# Description 

Le but de ce projet est de collecter, d'analyser et de visualiser les données de Covid-19 à partir de sources publiques telles que l'Organisation mondiale de la santé (OMS) ou les centres de contrôle et de prévention des maladies (CDC). On commence d'abord par collecter les données de Covid-19 et les stocker dans une base de données Cassandra,en utilisant les outils appropriés pour extraire les données et les charger dans la base de données. Ensuite, on indexe les données dans Elastic Search pour faciliter leur recherche et leur traitement. Enfin, on utilise Kibana pour visualiser les données de Covid-19 et créer des tableaux de bord interactifs pour suivre l'évolution de la pandémie. On utilisera les fonctionnalités de visualisation de Kibana pour créer des graphiques, des cartes et des diagrammes pour mieux comprendre les données.

# Commandes 

Commandes à faire dans le terminal sans le docker-compose : 

# Lancer le container elasticsearch

sudo docker run -d --rm -p 9200:9200 -p 9300:9300 -e "http.max_content_length= 1g" -e "discovery.type=single-node" -e "transport.host=127.0.0.1" -e ELASTIC_PASSWORD=secret --name elastic docker.elastic.co/elasticsearch/elasticsearch-platinum:6.0.0 && sleep 20

# Lancer le container kibana

sudo docker run -d --rm --link elastic:elastic-url -e "ELASTICSEARCH_URL=http://elastic-url:9200" -e ELASTICSEARCH_PASSWORD="secret" -p 5601:5601 --name kibana docker.elastic.co/kibana/kibana:6.0.0 && sleep 20

# Utiliser jq pour sérialiser le json obtenu grâce à python

cat confirmed.json | jq -c '.[] | {"index": {"_index": "confirmed_cases", "_type": "confirmed", "_id": .id}}, .' > confirmed.evo.json

cat deaths.json | jq -c '.[] | {"index": {"_index": "deaths_cases", "_type": "deaths", "_id": .id}}, .' > deaths.evo.json

cat recovered.json | jq -c '.[] | {"index": {"_index": "recovered_cases", "_type": "recovered", "_id": .id}}, .' > recovered.evo.json

# Indexation des données grâce à curl

curl -s -H "Content-Type: application/json" -XPOST "http://localhost:9200/confirmed/default/_bulk?pretty" -u 'elastic:secret' --data-binary @confirmed.evo.json

curl -s -H "Content-Type: application/json" -XPOST "http://localhost:9200/deaths/default/_bulk?pretty" -u 'elastic:secret' --data-binary @deaths.evo.json

curl -s -H "Content-Type: application/json" -XPOST "http://localhost:9200/recovered/default/_bulk?pretty" -u 'elastic:secret' --data-binary @recovered.evo.json

# Lancer Cassandra 

sudo docker run --name abdata-cassandra -p 7000:7000 -p 7001:7001 -p 7199:7199 -p 9042:9042 -p 9160:9160 -d cassandra:latest

# Docker compose

sudo docker-compose up 
