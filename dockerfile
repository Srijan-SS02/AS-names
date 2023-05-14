FROM python:3.6

WORKDIR /app
COPY . /app/

RUN pip install psycopg2==2.9.6
RUN pip install requests

CMD ["python3" , "asnames.py"]