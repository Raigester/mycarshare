FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media directory
RUN mkdir -p /app/media

# Run as non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
EXPOSE 8000
