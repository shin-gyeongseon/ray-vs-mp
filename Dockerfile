# Use official Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy benchmark script
COPY run_task_with_mp.py .

# Default command
CMD ["python", "run_task_with_mp.py"]