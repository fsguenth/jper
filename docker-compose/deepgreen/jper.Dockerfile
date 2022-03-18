FROM python:3.9-slim


RUN apt-get update
RUN apt-get install curl git -y

RUN mkdir -p /build /opt/jper
COPY . /build/jper
WORKDIR /build/jper
RUN pip3 install --upgrade -r requirements.txt
RUN pip3 install itsdangerous==2.0.1
RUN pip3 install WTForms==2.3.3
RUN mkdir -p /home/sftpusers
RUN mkdir -p /home/green
EXPOSE 5998
CMD ["bash", "/opt/jper/docker-compose/deepgreen/jper.entrypoint.sh"]
