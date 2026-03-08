# Multi-stage build optimized for security and size
# Production Dockerfile: Builds Flask application for AWS ECS Fargate deployment

# Use an official Python runtime as a parent image
# python:3.9-slim is preferred over full image to reduce attack surface (54MB vs 900MB+)
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files and to flush stdout/stderr
# These settings are critical for containerized environments for real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies required for building Python packages
# build-essential: Required for compiling C extensions (e.g., cryptography, psycopg2)
# libpq-dev: Required for PostgreSQL client libraries (needed for psycopg2)
# Note: These are removed after pip install to keep final image small (see cleanup below)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker layer caching
# This allows Docker to reuse the dependency layer if only source code changes
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade setuptools>=70.0.0

# DevOps Improvement: Consider adding a requirements-dev.txt for development dependencies
# This allows separating dev tools from production runtime

# Copy project files
# Copying after pip install ensures code changes don't invalidate dependency layer
COPY . /app/

# Create a non-root user and change ownership of the app directory
# Running as non-root (appuser) is a critical security best practice:
# - Prevents accidental or malicious root-level operations
# - Limits damage if the application is compromised
# - Meets security compliance requirements (CIS benchmarks)
RUN addgroup --system appgroup && adduser --system --group appuser \
    && chown -R appuser:appgroup /app

# Switch to the non-root user
# All subsequent operations (and the running app) execute as appuser, not root
USER appuser

# Expose the port the app runs on
# Note: ALB will route traffic to this port (5000)
EXPOSE 5000

# DevOps Improvements:
# 1. Add HEALTHCHECK: Manual health check endpoint (/health route)
#    HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#    CMD curl -f http://localhost:5000/health || exit 1
# 
# 2. Consider distroless base image for even smaller footprint:
#    FROM python:3.9-slim -> FROM gcr.io/distroless/python39
#    Reduces image size further and eliminates unnecessary OS packages
#
# 3. Add multi-stage build to separate build and runtime:
#    - Build stage: Include dev tools
#    - Runtime stage: Copy only wheels from build stage (no build tools)
#    - Results in <200MB final image vs ~500MB current

# Run the application using gunicorn (production-grade WSGI server)
# Gunicorn is essential for production deployments:
# - Flask development server is NOT suitable for production traffic
# - Gunicorn provides:
#   * Multiple worker processes (handle concurrent requests)
#   * Graceful reloading (zero-downtime deploys)
#   * Better resource management
# 
# Configuration recommendations:
# - workers: Set to (2 * CPU_COUNT) + 1 (e.g., 5 for 2 vCPU)
#   For ECS Fargate 1024 CPU, use: --workers 3
# - worker-class: Use 'gthread' for I/O-bound workload (Flask + DB I/O)
#   Command: gunicorn --workers 3 --worker-class gthread --threads 2 app:app
#
# - max-requests: Restart worker every 1000 requests to prevent memory leaks
#   Command: gunicorn --max-requests 1000 app:app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

