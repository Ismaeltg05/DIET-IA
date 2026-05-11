FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY ai/requirements.txt ./ai/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r ./ai/requirements.txt

# Copy application code
COPY ai/ ./ai/

# Health check
HEALTHCHECK --interval=15s --timeout=10s --retries=5 --start-period=10s \
    CMD curl -f http://localhost:8000/api/ai/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python3", "-m", "uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8000"]