# Use a lightweight Python image
FROM python:3.10-slim

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools for better compatibility
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Railway or Render will use
EXPOSE 8080

# Environment variable for Flask (optional but clean)
ENV PORT=8080

# Start the app using Gunicorn (production-ready)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--timeout", "300"]
