# Use an official Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project, including the virtual environment
COPY . .

# Expose the port that Django will use
EXPOSE 8000

# Default command to run the Django development server using your local virtual environment
CMD ["./venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
