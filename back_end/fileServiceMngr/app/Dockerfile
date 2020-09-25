FROM python:3.6

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY views.py /app
COPY sql_db.py /app
COPy sql_dbconf.py /app
CMD python views.py
