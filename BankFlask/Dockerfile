# Simple Dockerfile for the EduAI frontend + Flask app
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /usr/src/app

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]
