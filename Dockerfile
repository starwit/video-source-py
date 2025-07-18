FROM starwitorg/base-python-image:0.0.15 AS build

RUN apt update && apt install --no-install-recommends -y

ARG POETRY_VERSION
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Copy only files that are necessary to install dependencies
COPY poetry.lock poetry.toml pyproject.toml /code/

WORKDIR /code
RUN poetry install
    
# Copy the rest of the project
COPY . /code/


### Main artifact / deliverable image

FROM python:3.12-slim
RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0
    
COPY --from=build /code /code
WORKDIR /code

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Change ownership of the files to the non-root user
RUN chown -R appuser:appgroup /code

# Switch to non-root user
USER appuser

ENV PATH="/code/.venv/bin:$PATH"
CMD [ "python", "main.py" ]