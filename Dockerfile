# Use Python 3.9 as base image
FROM python:3.9-slim

# Install system dependencies for spotdl
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install spotdl
RUN pip install spotdl

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py Downloader.py SpotifyChecker.py ./
COPY templates ./templates/

# Create downloads directory with proper permissions
RUN mkdir -p downloads && chmod 777 downloads

# Create volume for persistent storage
VOLUME /app/downloads
VOLUME /app/data

# Move artists.json to data directory for persistence
ENV ARTIST_FILE=/app/data/artists.json

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]