# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Expose the Flask port
EXPOSE 5000

# Command to run the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
