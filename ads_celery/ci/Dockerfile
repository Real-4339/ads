FROM python:3.12.10-slim

WORKDIR /app

COPY ./ads_celery /app

RUN apt-get update && \
    apt-get install -y netcat-traditional iputils-ping

RUN pip install poetry==1.8.1

# Install Python dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root 

# Run the Celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]