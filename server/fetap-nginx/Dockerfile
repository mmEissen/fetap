FROM nginx:1.27.3

RUN rm /etc/nginx/conf.d/default.conf
COPY http.conf /etc/nginx/conf.d/http.conf

COPY static /usr/share/nginx/html