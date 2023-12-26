# Run the commands below to build and run the Docker image
# https://hub.docker.com/r/hashicorp/vault
# docker build -t matr-vault .
# docker run -d --cap-add=IPC_LOCK -p 8200:8200 matr-vault
# docker exec -it vault /bin/sh
# export VAULT_ADDR='http://127.0.0.1:8200'
# vault kv put secret/redis password="mypassword"

brew update upgrade
brew tap hashicorp/tap
brew install hashicorp/tap/vault

pip install --upgrade pip

export VAULT_ADDR='http://0.0.0.0:8200'
vault server -dev

Unseal Key: nX0tjLiwS0CifCmc3Jof4nDXWjFHnHavsq/bvW0pc+w=
Root Token: hvs.A4TyDtEEhqgE6ttJWSGvzVVM