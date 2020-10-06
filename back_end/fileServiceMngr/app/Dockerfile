FROM python:3.6

EXPOSE 5000

RUN apt-get update && apt-get install -y vim

WORKDIR /app

ADD . /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

CMD python views.py


