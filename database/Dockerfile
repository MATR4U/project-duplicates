# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest
# Create a user and group with a specific ID. Avoid using root (user ID 0)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# Switch to this new user
USER appuser
#Update OS
RUN apt-get update -y
#RUN apt-get upgrade -y
#RUN apt-get install -y nano

# Define environment variables for PostgreSQL
ENV POSTGRES_DB=mydb
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Expose the default PostgreSQL port (5432)
EXPOSE 5432

# Allow connections from anywhere.
#RUN sed -i -e"s/^#listen_addresses =.*$/listen_addresses = '*'/" /var/lib/postgresql/data/postgresql.conf
#RUN echo "host    all    all    0.0.0.0/0    md5" >> /var/lib/postgresql/data/pg_hba.conf

## Add init scripts
# ADD scripts /scripts
# ADD scripts/setup-my-schema.sh /docker-entrypoint-initdb.d/

# Optionally, add custom initialization scripts
# COPY init.sql /docker-entrypoint-initdb.d/
COPY docker-entrypoint-initdb.d/*.sql /docker-entrypoint-initdb.d/
#RUN chmod a+r /docker-entrypoint-initdb.d/*

#Switch to postgres user
#USER postgres

# Copy the custom pg_hba.conf file into the container
#COPY .conf/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf
#COPY .conf/postgresql.conf /var/lib/postgresql/data/postgresql.conf
#- /path/to/customPostgresql.conf:/var/lib/postgresql/data/postgresql.conf

# Restart server
#RUN /usr/lib/postgresql/15/bin/pg_ctl reload

# Set the working directory to /var/lib/postgresql/data
# WORKDIR /var/lib/postgresql/data

#COPY postgresql.conf      /tmp/postgresql.conf
#COPY updateConfig.sh      /docker-entrypoint-initdb.d/_updateConfig.sh