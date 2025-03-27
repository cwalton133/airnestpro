# Use a Python base image
FROM python:3.11

# Install system dependencies for Pillow and other libraries
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the port Django runs on
EXPOSE 8000

# Run the Django server using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project.wsgi:application"]
