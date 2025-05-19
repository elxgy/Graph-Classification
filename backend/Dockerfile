FROM python:3.9-slim

# Create and set working directory
WORKDIR /app

# Install system dependencies if needed (uncomment if using additional packages)
# RUN apt-get update && apt-get install -y build-essential --no-install-recommends \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the Flask port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=routes.py
ENV FLASK_RUN_HOST=0.0.0.0

# Default command to run the API
CMD ["flask", "run"]
