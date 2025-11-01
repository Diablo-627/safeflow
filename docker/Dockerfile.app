# docker/Dockerfile.app
FROM python:3.11-slim

# system deps for some python packages (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# create non-root user
ENV APP_USER=appuser
RUN useradd --create-home --shell /bin/bash $APP_USER

WORKDIR /app

# copy only requirements first for better caching
COPY safeflow/app/requirements.txt /app/requirements.txt

# install deps
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -r /app/requirements.txt

# copy project (use full repo mount in docker-compose for dev, but keep copy for image)
COPY . /app

# ensure permissions
RUN chown -R $APP_USER:$APP_USER /app
USER $APP_USER

ENV PYTHONPATH=/app/safeflow

EXPOSE 8000

# use uvicorn via module (safer)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
