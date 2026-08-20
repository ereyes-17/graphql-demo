FROM python:3.10.21-alpine3.24

WORKDIR /opt/app

COPY app ./app
COPY requirements.txt .

RUN python -m pip install -r requirements.txt

EXPOSE 8000

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]