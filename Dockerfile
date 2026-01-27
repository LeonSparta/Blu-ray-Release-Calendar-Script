FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app

# Run with Gunicorn (production) or Flask (dev)
# For simplicity in this script, we use flask run
CMD ["flask", "run", "--host=0.0.0.0"]
