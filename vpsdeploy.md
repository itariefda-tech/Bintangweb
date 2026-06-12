cd /opt/apps/Bintangweb
docker rm -f bintangweb-app
docker run -d \
  --name bintangweb-app \
  --restart unless-stopped \
  --network hosting_web \
  --env-file /opt/apps/Bintangweb/.env \
  -v bintangweb-app-data:/app/data \
  -p 5080:5080 \
  bintangweb-app:latest