FROM python:3.12.10-slim

WORKDIR /app

COPY ./visualization/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./visualization .

EXPOSE 8050 

CMD ["python", "app.py"]