FROM python:3.13-alpine

WORKDIR /app
COPY app.py ./app.py
USER 10001:10001
EXPOSE 8000
CMD ["python3", "-u", "app.py"]
