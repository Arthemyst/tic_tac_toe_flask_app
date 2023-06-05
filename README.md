# flask_app
start docker:
docker-compose -f docker/docker-compose.yaml up --build

docker cp create_table.sql docker-database-1:/create_table.sql
docker exec -it docker-database-1 psql -U postgres -d postgres -f /create_table.sql
check docker-database-1 ip and put it inside .env variable: 
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' docker-database-1
