FROM python:alpine3.12
LABEL authors="alexeypopkov"

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
