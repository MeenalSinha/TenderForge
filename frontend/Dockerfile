# ==============================================================================
# TenderForge Frontend - Production Multi-Stage Dockerfile
# ==============================================================================

# Stage 1: Build (if needed)
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
COPY . .

# Stage 2: Nginx Web Server
FROM nginx:1.27-alpine AS runtime

COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
