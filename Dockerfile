FROM golang:1.13 as builder
FROM python:3.8-slim
RUN apt-get update
RUN apt-get install -y git
# RUN which git && echo "DONDE ESTA INSTALADO GIT"
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install dbt-bigquery
ENV DBT_PROFILES_DIR=/app/
WORKDIR /app/
COPY . /app/
RUN CGO_ENABLED=0 GOOS=linux go build -v -o server
ENTRYPOINT "./server"