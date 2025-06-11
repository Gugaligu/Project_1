FROM nginx:alpine

# Удалим дефолтный index.html
RUN rm -rf /usr/share/nginx/html/*

# Копируем наш YAML и HTML в контейнер
COPY index.html /usr/share/nginx/html/
COPY swagger.yaml /usr/share/nginx/html/
