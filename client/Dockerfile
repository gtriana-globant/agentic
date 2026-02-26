# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for building certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create a non-privileged user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy installed python packages from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Ensure the appuser owns the application directory
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Expose FastAPI default port
EXPOSE 8080

# Use uvicorn to run the FastAPI app
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8080"]