#!/bin/sh
set -u

failed_checks=""

run_check() {
  check_name=$1
  shift

  printf '\n==> %s\n' "$check_name"
  if "$@"; then
    printf 'PASS: %s\n' "$check_name"
  else
    check_status=$?
    printf 'FAIL: %s (exit %s)\n' "$check_name" "$check_status"
    if [ -n "$failed_checks" ]; then
      failed_checks="$failed_checks, "
    fi
    failed_checks="${failed_checks}${check_name} (exit ${check_status})"
  fi
}

run_check "Ruff" uv run ruff check .
run_check "basedpyright" uv run basedpyright
run_check "codespell" uv run codespell --skip=node_modules .

run_vale() {
  git ls-files --cached --others --exclude-standard -z -- \
    '*.md' '*.rst' '*.adoc' '*.txt' ':(exclude).vale/**' \
    | xargs -0 vale --minAlertLevel=error --output=line
}

run_check "Vale (errors only, gitignore-aware)" run_vale

if [ -n "$failed_checks" ]; then
  printf '\nFailed checks: %s\n' "$failed_checks"
  exit 1
fi

printf '\nAll linters passed.\n'
