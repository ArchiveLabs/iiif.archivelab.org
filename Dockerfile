FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /iiify
WORKDIR /iiify
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
EXPOSE 8080
CMD ["/iiify/iiify/app.py"]
