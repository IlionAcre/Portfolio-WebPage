FROM python:3.11.0-slim-buster

WORKDIR /portfolio-webpage

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

COPY ./static /app/static

CMD ["python3", "main.py"]