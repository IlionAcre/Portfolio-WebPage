FROM python:3.11.0-slim-buster

WORKDIR /portfolio-webpage

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "main:app"]