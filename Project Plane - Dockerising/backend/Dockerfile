FROM python:3.11.9-slim AS base

WORKDIR /Project_plane_build/backend

COPY requirements_Backend.txt .

RUN pip install -r requirements_Backend.txt

COPY . . 

CMD [ "python", "Backend.py" ]