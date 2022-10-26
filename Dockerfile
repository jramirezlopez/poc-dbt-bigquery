FROM python:3.8-slim
FROM golang:1.13 as builder
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install dbt-bigquery
WORKDIR /app
COPY invoke.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -v -o server

USER root
WORKDIR /dbt
COPY --from=builder /app/server ./
COPY script.sh ./
COPY . ./

ENTRYPOINT "./server"