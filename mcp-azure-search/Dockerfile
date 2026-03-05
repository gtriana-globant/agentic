# Stage 1: Build Stage (Install dependencies without bloating the final image)
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and allow real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools if necessary (gcc/g++ for specific python extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a specific prefix directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Production Stage (Lean final image)
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /install /usr/local
# Copy the application source code
COPY . .

# --- SECURITY BEST PRACTICES ---
# Create a non-root user to run the process (defense in depth)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose the port used by FastMCP (usually 8000 in server mode)
EXPOSE 8000
RUN ls -l

# Execution Command
# Ensure your script is named 'main.py' or update accordingly
CMD ["python", "server.py"]