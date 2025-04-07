FROM python:3.11-slim
LABEL authors="alexeypopkov"

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends python3-pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
