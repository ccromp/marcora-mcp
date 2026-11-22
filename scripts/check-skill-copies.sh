#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SOURCE_DIR="skill/marcora-mcp"
COPIES=(
  "plugin/skills/marcora-mcp"
  "directories/cursor/marcora/skills/marcora-mcp"
)

if [[ ! -d "$SOURCE_DIR" || -L "$SOURCE_DIR" ]]; then
  echo "FAIL: canonical skill directory missing or is a symlink: $SOURCE_DIR" >&2
  exit 1
fi

plugin_symlinks="$(find plugin -type l 2>/dev/null || true)"
if [[ -n "$plugin_symlinks" ]]; then
  echo "FAIL: symbolic link(s) found inside plugin/ (disallowed by Claude plugin directory):" >&2
  echo "$plugin_symlinks" >&2
  exit 1
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_plugin_symlinks="$(git ls-files -s plugin/ | grep '^120000' || true)"
  if [[ -n "$git_plugin_symlinks" ]]; then
    echo "FAIL: tracked symlink(s) found in git index under plugin/:" >&2
    echo "$git_plugin_symlinks" >&2
    exit 1
  fi
fi

failed=0
for copy in "${COPIES[@]}"; do
  if [[ -L "$copy" ]]; then
    echo "FAIL: $copy is a symbolic link; must be a real copy of $SOURCE_DIR" >&2
    failed=1
    continue
  fi
  if [[ ! -d "$copy" ]]; then
    echo "FAIL: $copy is missing; must be a real copy of $SOURCE_DIR" >&2
    failed=1
    continue
  fi
  if ! diff -ru "$SOURCE_DIR" "$copy"; then
    echo "FAIL: $copy differs from $SOURCE_DIR" >&2
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  cat >&2 <<'EOF'

To resync both copies from committed skill/marcora-mcp:
  rm -rf plugin/skills/marcora-mcp directories/cursor/marcora/skills/marcora-mcp
  git archive HEAD skill/marcora-mcp | tar -x -C plugin/skills --strip-components=1
  git archive HEAD skill/marcora-mcp | tar -x -C directories/cursor/marcora/skills --strip-components=1
EOF
  exit 1
fi

echo "OK: plugin/ and directories/cursor/ skill copies match $SOURCE_DIR with no symlinks under plugin/"
