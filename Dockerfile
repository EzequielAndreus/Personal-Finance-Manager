# Base image: Ubuntu with Python
FROM python:3.13-slim

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies
RUN apt-get update && \
    apt-get install -y python3 curl && \
    apt-get clean

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Copy project files into the container
COPY . /app

# Install dependencies
RUN uv sync

# Expose Flask port
EXPOSE 5001

# Command to run the application
CMD ["python3", "src/app.py"]
