# Use the official Vault image as a base
FROM hashicorp/vault:latest

# The Vault server listens on port 8200 by default, expose this port
EXPOSE 8200

# By default, Vault will run in server mode
ENTRYPOINT ["vault", "server"]

# By default, we'll use the dev server
CMD ["-dev"]