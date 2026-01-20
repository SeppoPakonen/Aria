FROM python:3.11-slim

# Install dependencies for Chrome/Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY plugins/ /app/plugins/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV ARIA_HOME=/root/.aria
ENV ARIA_LOG_LEVEL=INFO

# Create Aria home directory
RUN mkdir -p /root/.aria/scripts /root/.aria/plugins /root/.aria/reports

# Default command
ENTRYPOINT ["python3", "src/aria.py"]
CMD ["--help"]
