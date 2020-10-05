FROM python:3.6

EXPOSE 4500

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY mongo_db/mongo_db.py /app
COPY mongo_db/mongo_dbconf.py /app
COPY sql_db/sql_db.py /app
COPY sql_db/sql_dbconf.py /app
COPY views.py /app
CMD python views.py
