# Use a lightweight Python version
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Command to run the app
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]