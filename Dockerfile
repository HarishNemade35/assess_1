# FROM python:3.10-slim
FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /PROJECT

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Copy Pipfile and lock file
COPY ./PROJECT/Pipfile ./PROJECT/Pipfile.lock ./

# Install dependencies using Pipenv
RUN pip install pipenv 

RUN  pipenv install --system --deploy

# Copy app files
COPY ./PROJECT .

# Expose the FastAPI default port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
