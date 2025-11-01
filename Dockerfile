FROM python:3.10-slim

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose port 8080 (Render uses this by default)
EXPOSE 8080

# Run the Flask app using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
