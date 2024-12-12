FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY . .

ENV UVICORN_CMD="uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

EXPOSE 8000

CMD ["sh", "-c", "/wait-for-it.sh redis:6379 -- uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
