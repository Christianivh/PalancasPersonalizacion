FROM ubuntu:16.04

COPY requirements.txt /tmp
COPY script-run.sh /tmp
COPY CLARA_CLUST.py /home
COPY healthcheck.py /home
COPY /predict /home/predict
COPY /training /home/training
COPY /queries /home/queries

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates && \
	apt-get install lsb-release -y && apt-get install python3 -y && \
	apt install python3-pip -y && apt-get install libpq-dev -y

WORKDIR /tmp
RUN pip3 install -r requirements.txt

RUN pip3 install --upgrade google-cloud-bigquery[pandas] && \ 
	pip3 install --upgrade google-cloud-bigquery-storage[fastavro,pandas]

RUN apt-get install python-tk -y && apt-get install python-psycopg2 -y && \
	apt-get install -y git

RUN chmod +x script-run.sh
ENTRYPOINT ["bash","./script-run.sh"]
CMD []
