FROM python:3.7-slim

WORKDIR /app

RUN python3 -m pip install --upgrade pip
COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir
RUN mv redoc.yaml static/

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
