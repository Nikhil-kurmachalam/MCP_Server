# Use a lightweight Python image
FROM python:3.11-slim

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY main.py .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Command to run the MCP server
CMD ["python", "main.py"]