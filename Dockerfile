# Base image optimized for ARM64
FROM python:3.10-slim-bullseye as build

# Install system dependencies
RUN apt update && apt install --no-install-recommends -y \
    curl \
    git \
    python3-dev \
    gcc \
    g++ \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    libjpeg-dev

# Install Poetry
ARG POETRY_VERSION
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /code

# Copy dependency files first for caching
COPY poetry.lock poetry.toml pyproject.toml /code/

# Install dependencies
RUN poetry install --no-root


# Copy the rest of the project
COPY . /code/


### **Final Image for Execution**
FROM python:3.10-slim-bullseye

# Install runtime dependencies
RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0 \
    libjpeg-turbo-progs \
    python3-opencv \
    ffmpeg

# Copy built dependencies from the build stage
COPY --from=build /code /code

# Set working directory
WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

# Default command to run the application
CMD [ "python", "main.py" ]
