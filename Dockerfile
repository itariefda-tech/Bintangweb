FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY scripts ./scripts
COPY assets ./assets
COPY css ./css
COPY js ./js
COPY src ./src
COPY index.html owner-builder.html robots.txt sitemap.xml site.webmanifest ./

RUN npm run build

FROM python:3.12-alpine

WORKDIR /app

COPY app.py marketplace_auth.py ./
COPY --from=builder /app/dist/ ./public/

RUN mkdir -p /app/data

ENV HOST=0.0.0.0 \
    PORT=5080 \
    PUBLIC_ROOT=/app/public \
    DATA_ROOT=/app/data

EXPOSE 5080

VOLUME ["/app/data"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:5080/health || exit 1

CMD ["python", "app.py"]
