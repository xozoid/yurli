#!/bin/sh
set -u

failed_formatters=""

run_formatter() {
  formatter_name=$1
  shift

  printf '\n==> %s\n' "$formatter_name"
  if "$@"; then
    printf 'PASS: %s\n' "$formatter_name"
  else
    formatter_status=$?
    printf 'FAIL: %s (exit %s)\n' "$formatter_name" "$formatter_status"
    if [ -n "$failed_formatters" ]; then
      failed_formatters="$failed_formatters, "
    fi
    failed_formatters="${failed_formatters}${formatter_name} (exit ${formatter_status})"
  fi
}

run_formatter "Ruff format" uv run ruff format .
run_formatter "Prettier" npm exec --no -- prettier --write .
run_formatter "Taplo" uv run taplo fmt '*.toml'
run_formatter "YAML" uv run prek run yamlfmt --all-files

if [ -n "$failed_formatters" ]; then
  printf '\nFailed formatters: %s\n' "$failed_formatters"
  exit 1
fi

printf '\nAll formatters passed.\n'
