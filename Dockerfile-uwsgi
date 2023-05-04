FROM tiangolo/uwsgi-nginx-flask:python3.11
ENV LISTEN_PORT 8080
EXPOSE 8080
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
COPY ./nginx-vhost.conf /etc/nginx/conf.d/nginx.conf
