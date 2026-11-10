#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(git -C "$script_dir" rev-parse --show-toplevel)
cd "$repo_root"

upgrade=0
case "${1-}" in
  "") ;;
  --upgrade) upgrade=1 ;;
  *)
    printf 'Usage: %s [--upgrade]\n' "$0" >&2
    exit 2
    ;;
esac
if [ "$#" -gt 1 ]; then
  printf 'Usage: %s [--upgrade]\n' "$0" >&2
  exit 2
fi

if ! command -v uv >/dev/null 2>&1; then
  printf 'uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/\n' >&2
  exit 1
fi

install_vale() {
  if command -v vale >/dev/null 2>&1; then
    return
  fi

  if command -v brew >/dev/null 2>&1; then
    brew install vale
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y vale
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --needed vale
  elif command -v snap >/dev/null 2>&1; then
    sudo snap install vale
  elif command -v go >/dev/null 2>&1; then
    go install github.com/vale-cli/vale/v3/cmd/vale@latest
    PATH="$PATH:$(go env GOPATH)/bin"
    export PATH
  else
    printf 'Install Vale using the instructions at https://vale.sh/docs/ before retrying.\n' >&2
    return 1
  fi
}

printf 'Syncing Python environment...\n'
if [ "$upgrade" -eq 1 ]; then
  uv lock --upgrade
fi
uv sync --locked --all-groups
uv run prek install

printf 'Installing Vale if needed...\n'
install_vale
vale sync

printf 'Installing npm dependencies...\n'
if ! command -v npm >/dev/null 2>&1; then
  printf 'npm is required. Install Node.js 24 or later, then retry.\n' >&2
  exit 1
fi
npm ci

for env_file in .env .env.leave; do
  if [ ! -e "$env_file" ]; then
    case "$env_file" in
      .env) printf '%s\n' '. .venv/bin/activate' > "$env_file" ;;
      .env.leave) printf '%s\n' 'deactivate' > "$env_file" ;;
    esac
    printf 'Created %s\n' "$env_file"
  else
    printf 'Preserved existing %s\n' "$env_file"
  fi
done

printf '\nEnvironment setup is complete.\n'
