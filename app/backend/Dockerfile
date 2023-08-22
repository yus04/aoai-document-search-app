# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /code

COPY backend/requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "app_test:app"]

# # syntax=docker/dockerfile:1

# FROM python:3.11

# WORKDIR /app/backend

# COPY backend/requirements.txt .

# RUN pip3 install -r requirements.txt

# COPY . .

# EXPOSE 8000

# ENTRYPOINT ["gunicorn", "app:app"]