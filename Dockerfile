# --- STAGE 1: Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and allow real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools for C-extensions if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a specific prefix directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- STAGE 2: Production Stage ---
FROM python:3.11-slim

WORKDIR /app

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Ensure the app can find the modules in the current directory
ENV PYTHONPATH=/app 

# Copy only the installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the application source code (core, services, tools, main.py)
# This will copy your new folder structure: /app/core, /app/services, etc.
COPY . .

# --- SECURITY BEST PRACTICES ---
# Create a non-root user for security (required for many AKS policies)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose the FastMCP SSE port
EXPOSE 8000

# --- EXECUTION ---
# Updated to point to main.py instead of server.py
CMD ["python", "main.py"]