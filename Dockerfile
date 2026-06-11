FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY scripts ./scripts
COPY assets ./assets
COPY css ./css
COPY js ./js
COPY index.html robots.txt sitemap.xml site.webmanifest ./

RUN npm run build

FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf && \
    printf '%s\n' \
      'server {' \
      '    listen 5080;' \
      '    listen [::]:5080;' \
      '    server_name _;' \
      '' \
      '    root /usr/share/nginx/html;' \
      '    index index.html;' \
      '' \
      '    gzip on;' \
      '    gzip_vary on;' \
      '    gzip_min_length 1024;' \
      '    gzip_types text/plain text/css application/javascript application/json application/xml image/svg+xml;' \
      '' \
      '    location / {' \
      '        add_header Cache-Control "no-cache";' \
      '        try_files $uri $uri/ /index.html;' \
      '    }' \
      '' \
      '    location ~* \.[0-9a-f]{12}\.min\.(?:css|js)$ {' \
      '        expires 1y;' \
      '        add_header Cache-Control "public, max-age=31536000, immutable";' \
      '        try_files $uri =404;' \
      '    }' \
      '' \
      '    location ~* \.(?:jpg|jpeg|gif|png|svg|webp|ico|mp3|woff2?)$ {' \
      '        expires 30d;' \
      '        add_header Cache-Control "public, max-age=2592000";' \
      '        try_files $uri =404;' \
      '    }' \
      '' \
      '    location = /health {' \
      '        access_log off;' \
      '        add_header Content-Type text/plain;' \
      '        return 200 "ok\n";' \
      '    }' \
      '}' \
      > /etc/nginx/conf.d/bintangweb.conf

COPY --from=builder /app/dist/ /usr/share/nginx/html/

EXPOSE 5080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:5080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
