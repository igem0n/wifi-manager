# Use a lightweight Python image as the base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libsystemd-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install systemd and necessary tools
RUN apt-get update && apt-get install -y \
    systemd \
    hostapd \
    isc-dhcp-server \
    net-tools \
    iproute2 \
    && apt-get clean

# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies and debugpy
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install debugpy
# Copy the rest of the application files
COPY . .

# Expose the application port (default Flask or your app's port) and debug port
EXPOSE 8000 5680

# Set environment variables for Flask and debugpy
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development

# Start the Gunicorn server with debugpy
# Start Gunicorn with debugpy, waiting for the debugger to attach
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5680", "--wait-for-client", \
     "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", \
     "app:app"]
