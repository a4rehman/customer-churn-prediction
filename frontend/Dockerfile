# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine AS serve
# NGINX_ENVSUBST_FILTER whitelists which env var gets substituted into the template,
# so nginx's own $host/$uri variables stay intact.
ENV BACKEND_UPSTREAM=http://backend:8000 \
    NGINX_ENVSUBST_FILTER=BACKEND_UPSTREAM
COPY deploy/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
CMD ["nginx", "-g", "daemon off;"]
