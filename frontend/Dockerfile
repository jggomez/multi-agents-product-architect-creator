FROM nginx:alpine

# Remove default nginx static content
RUN rm -rf /usr/share/nginx/html/*

# Copy static frontend files
COPY index.html /usr/share/nginx/html/
COPY js/ /usr/share/nginx/html/js/
COPY styles/ /usr/share/nginx/html/styles/

# Custom nginx config for Cloud Run (listen on PORT env var)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Entrypoint script to inject environment variables at runtime
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
