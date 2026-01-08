#!/usr/bin/env bash
set -euo pipefail

echo "WARNING: This script uses a HEURISTIC to guess the most active Chromium/Chrome profile (by last-modified timestamps)."
echo "WARNING: Heuristics can be wrong. Double-check the chosen user/profile before relying on it."
echo

PORT="${PORT:-9222}"

# Pick a browser binary (prefer Chromium on Linux, but allow Google Chrome if present).
CHROME_BIN="${CHROME_BIN:-}"
if [[ -z "${CHROME_BIN}" ]]; then
  if command -v chromium >/dev/null 2>&1; then
    CHROME_BIN="chromium"
  elif command -v chromium-browser >/dev/null 2>&1; then
    CHROME_BIN="chromium-browser"
  elif command -v google-chrome >/dev/null 2>&1; then
    CHROME_BIN="google-chrome"
  elif command -v google-chrome-stable >/dev/null 2>&1; then
    CHROME_BIN="google-chrome-stable"
  else
    echo "ERROR: Could not find a Chromium/Chrome binary (chromium/chromium-browser/google-chrome)."
    exit 1
  fi
fi

# Candidate user-data roots to scan across users (root can see all; if not root, it will likely only see its own).
# Chromium: ~/.config/chromium
# Chrome:   ~/.config/google-chrome
roots=()

add_root_if_exists() {
  local p="$1"
  [[ -d "$p" ]] && roots+=("$p")
}

# Scan /home/* and /root
for d in /home/*; do
  [[ -d "$d" ]] || continue
  add_root_if_exists "$d/.config/chromium"
  add_root_if_exists "$d/.config/google-chrome"
done
add_root_if_exists "/root/.config/chromium"
add_root_if_exists "/root/.config/google-chrome"

if [[ ${#roots[@]} -eq 0 ]]; then
  echo "ERROR: No Chromium/Chrome profile roots found under /home/* or /root."
  echo "       Expected ~/.config/chromium or ~/.config/google-chrome."
  exit 1
fi

# Find the newest profile among all candidate roots.
best_profile_path=""
best_profile_mtime=0
best_root=""

profile_dirs_for_root() {
  local root="$1"
  # Common profile dirs: Default, Profile *
  shopt -s nullglob
  local dirs=( "$root"/Default "$root"/Profile\ * )
  shopt -u nullglob
  for p in "${dirs[@]}"; do
    [[ -d "$p" ]] || continue
    # Use Preferences as signal for "real profile"
    [[ -f "$p/Preferences" ]] || continue
    echo "$p"
  done
}

mtime_of_profile() {
  local p="$1"
  # Prefer Preferences mtime, else directory mtime
  if [[ -f "$p/Preferences" ]]; then
    stat -c %Y "$p/Preferences" 2>/dev/null || echo 0
  else
    stat -c %Y "$p" 2>/dev/null || echo 0
  fi
}

for root in "${roots[@]}"; do
  while IFS= read -r prof; do
    mtime="$(mtime_of_profile "$prof")"
    if [[ "$mtime" -gt "$best_profile_mtime" ]]; then
      best_profile_mtime="$mtime"
      best_profile_path="$prof"
      best_root="$root"
    fi
  done < <(profile_dirs_for_root "$root")
done

if [[ -z "$best_profile_path" ]]; then
  echo "ERROR: Found profile roots, but could not find any valid profiles (Default/Profile *) with a Preferences file."
  exit 1
fi

PROFILE_NAME="$(basename "$best_profile_path")"
USER_DATA_DIR="$best_root"

# Derive the owning user from the path, best-effort.
TARGET_USER="root"
if [[ "$USER_DATA_DIR" == /home/* ]]; then
  TARGET_USER="$(echo "$USER_DATA_DIR" | awk -F/ '{print $3}')"
fi

echo "Selected (heuristic):"
echo "  Browser binary : $CHROME_BIN"
echo "  User data dir  : $USER_DATA_DIR"
echo "  Profile dir    : $PROFILE_NAME"
echo "  Target user    : $TARGET_USER"
echo "  Debug port     : $PORT"
echo
echo "NOTE: Close other Chromium/Chrome instances using this same profile, or the browser may refuse to start / will create lock conflicts."
echo

# Build command
cmd=( "$CHROME_BIN"
  "--remote-debugging-port=$PORT"
  "--user-data-dir=$USER_DATA_DIR"
  "--profile-directory=$PROFILE_NAME"
  "--no-first-run"
  "--no-default-browser-check"
)

# If running as root, Chromium typically requires --no-sandbox; but we prefer to run as the profile owner.
if [[ "$(id -u)" -eq 0 && "$TARGET_USER" != "root" ]]; then
  if command -v runuser >/dev/null 2>&1; then
    echo "Launching as user '$TARGET_USER' via runuser..."
    exec runuser -u "$TARGET_USER" -- "${cmd[@]}"
  else
    echo "Launching as user '$TARGET_USER' via su..."
    exec su - "$TARGET_USER" -c "$(printf '%q ' "${cmd[@]}")"
  fi
else
  if [[ "$(id -u)" -eq 0 ]]; then
    echo "Running as root. If Chromium refuses to start, consider running this script as the target user instead."
    echo "As a last resort you can export EXTRA_CHROME_FLAGS='--no-sandbox' and rerun."
  fi
  # Allow optional extra flags
  if [[ -n "${EXTRA_CHROME_FLAGS:-}" ]]; then
    # shellcheck disable=SC2206
    extra=( $EXTRA_CHROME_FLAGS )
    cmd+=( "${extra[@]}" )
  fi
  exec "${cmd[@]}"
fi
