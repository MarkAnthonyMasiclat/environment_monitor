FROM python:3.12-slim

WORKDIR /app
COPY pi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pi/subscriber ./subscriber
COPY shared ./shared

CMD ["python", "-m", "subscriber.app"]
