FROM python:3.11

COPY . /app/

WORKDIR /app

RUN python -m pip install -r requirements.txt
RUN chmod +x wait-for-it.sh