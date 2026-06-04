FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Security Best Practice: Do not run containers as root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8080

CMD ["python", "main.py"]
