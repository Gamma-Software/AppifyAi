docker build -t generative-app .
docker stop generative-app
docker rm generative-app
docker compose -f "docker-compose.yml" up -d --build