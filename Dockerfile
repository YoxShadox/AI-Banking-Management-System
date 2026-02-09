FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY BankFlask/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Flask app
COPY BankFlask/ .

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "run.py"]
