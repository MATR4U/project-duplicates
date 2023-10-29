
# Use the lightweight Alpine Linux as a base image
FROM alpine:latest

# Install sqlite
RUN apk add --no-cache sqlite

# Create a directory for the SQLite database
WORKDIR /data

# Set the entry point to sqlite3
ENTRYPOINT ["sqlite3"]
