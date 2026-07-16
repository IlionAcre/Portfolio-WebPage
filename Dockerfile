FROM python:3.11.0-slim-buster

WORKDIR /portfolio-webpage

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]