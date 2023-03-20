FROM python:3.10-alpine

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

STOPSIGNAL SIGINT
CMD python main.py