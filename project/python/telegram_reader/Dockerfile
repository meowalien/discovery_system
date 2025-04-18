# Use an official Python runtime as a parent image
FROM python:3.12.7-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building psycopg2 and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .


# Set an environment variable for the configuration file, if needed
ENV CONFIG_FILE=config.yml

# Run the server using Uvicorn
CMD ["python", "main.py"]