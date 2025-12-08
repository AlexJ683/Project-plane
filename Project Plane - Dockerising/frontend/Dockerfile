FROM python:3.11.9-slim AS base

WORKDIR /Project_plane_build/frontend

COPY requirements_Frontend.txt .

RUN pip install -r requirements_Frontend.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]

