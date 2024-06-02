# Dockerfile
FROM python:3.11-slim

# Create a directory for the application
WORKDIR /app

# Copy the script that will run the code
COPY ./run_code.py /app

# Install any dependencies (if necessary)
RUN pip install --no-cache-dir numpy pandas

# Command to run when the container starts
#CMD ["python", "run_code.py"]