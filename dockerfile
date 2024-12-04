# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install flask requests

# Expose the port Flask app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]