# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# ENV STATIC_ROOT /code/static

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container at /code
COPY requirements.txt /code/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install libmagic dependencies
RUN apt-get update && apt-get install -y \
    libmagic-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /code
COPY . /code/

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the port that the Django app will run on
# EXPOSE 8000

# Set the environment variable for the port
ENV PORT=8000

# Run the Django application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "resume_builder.wsgi:application"]