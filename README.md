# Projet_elasticsearch

Le projet a pour objectif de prendre des données sur le covid (les cas confirmés, les cas de decès et les cas de rétablissements) et grâce à une ETL réalisée par un script python.
Le script prend les données en question qui sont contenu dans un csv et les met dans un dataframe pandas. Puis ensuite fait une transformation des données pour tout normalisé et enfin charge ces données dans ElasticSearch et puis dans Cassandra.
Toutes les étapes du projet est automatisé avec un docker-compose et un Dockerfile.

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
