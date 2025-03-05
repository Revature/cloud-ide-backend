#!/usb/bin/bash
set -e

echo "$SSH_PRIVATE_KEY"
echo "$SSH_HOST"
echo "$SSH_PORT"
echo "$SSH_USER"
echo "$DOCKER_COMPOSE_PREFIX"

log() {
  echo ">> [local]" $@
}

log "Launching ssh agent."
eval `ssh-agent -s`

ssh-add <(echo "$SSH_PRIVATE_KEY")

scp -P "$SSH_PORT" ./docker-compose.yml "$SSH_USER@$SSH_HOST":~/workspace/docker-compose.yml

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  "$SSH_USER@$SSH_HOST" -p "$SSH_PORT" \
  "docker compose -f \"$DOCKER_COMPOSE_FILENAME\" -p \"$DOCKER_COMPOSE_PREFIX\" pull" \

set +e
ssh-agent -k