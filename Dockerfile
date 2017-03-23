# docker build -t telminov/ansible-manager .
FROM ubuntu:16.04
MAINTAINER telminov <telminov@soft-way.biz>


RUN apt-get update && \
    apt-get install -y \
                    supervisor \
                    python3-pip

RUN mkdir /var/log/ansible-manager/

COPY . /opt/ansible-manager
WORKDIR /opt/ansible-manager


RUN pip3 install -r requirements.txt
RUN cp project/local_settings.sample.py project/local_settings.py

COPY supervisor/prod.conf /etc/supervisor/conf.d/ansible-manager.conf

EXPOSE 80
VOLUME /data/
VOLUME /conf/
VOLUME /static/
