# Use the lightweight Alpine Linux as a base.py image
FROM alpine:latest

ENV APP_ENV=/app
ENV VENV=$APP_ENV/.venv
ENV PATH="$VENV/bin:$PATH"
# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED True
ENV POSTGRES_PASSWORD: my_password

# Update the package repository and install necessary packages
RUN apk update
RUN apk upgrade
RUN apk add --no-cache curl
RUN apk add --no-cache build-base
RUN apk add --no-cache python3
RUN apk add --no-cache py3-pip
RUN apk add --no-cache python3-dev
RUN apk add --no-cache postgresql-dev
RUN apk add --no-cache openblas-dev
RUN apk add --no-cache lapack-dev
RUN apk add --no-cache libffi-dev
RUN apk add --no-cache openssl-dev
RUN apk add --no-cache cairo-dev

# Create a user and group with a specific ID. Avoid using root (user ID 0)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN mkdir -p $APP_ENV

# Set the working directory
WORKDIR $APP_ENV

# Copy application code into the container
COPY . .
RUN chown -R appuser:appgroup $APP_ENV
RUN chmod -R u+rwx .

# Switch to this new user
USER appuser

# Create and activate a virtual environment
RUN python3 -m venv $VENV
# Upgrade pip within the virtual environment with --no-cache-dir
RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN source $VENV/bin/activate

# Install project dependencies (use pip3 to install packages)
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Expose the desired port
EXPOSE 8000
EXPOSE 5432

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
CMD curl -f http://localhost:80/ || exit 1

# Run the Uvicorn server directly
#CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD [ "python3", "main.py" ]

# Run the application and API
# RUN python3 -m uvicorn app_api:app --reload
#CMD ["python3", "main.py", "/data/DataSource", "/data/DataTarget"]
