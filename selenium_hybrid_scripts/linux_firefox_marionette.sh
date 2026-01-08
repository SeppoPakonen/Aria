#!/usr/bin/env bash
set -euo pipefail

echo "WARNING: This script uses a HEURISTIC to guess the most active Firefox profile (by last-modified timestamps)."
echo "WARNING: Heuristics can be wrong. Double-check the chosen user/profile before relying on it."
echo

FIREFOX_BIN="${FIREFOX_BIN:-}"
if [[ -z "${FIREFOX_BIN}" ]]; then
  if command -v firefox >/dev/null 2>&1; then
    FIREFOX_BIN="firefox"
  elif command -v firefox-esr >/dev/null 2>&1; then
    FIREFOX_BIN="firefox-esr"
  else
    echo "ERROR: Could not find Firefox binary (firefox/firefox-esr)."
    exit 1
  fi
fi

# Candidate roots:
#   ~/.mozilla/firefox (contains Profiles/ and profiles.ini)
roots=()

add_root_if_exists() {
  local p="$1"
  [[ -d "$p" ]] && roots+=("$p")
}

for d in /home/*; do
  [[ -d "$d" ]] || continue
  add_root_if_exists "$d/.mozilla/firefox"
done
add_root_if_exists "/root/.mozilla/firefox"

if [[ ${#roots[@]} -eq 0 ]]; then
  echo "ERROR: No Firefox profile roots found under /home/* or /root."
  echo "       Expected ~/.mozilla/firefox."
  exit 1
fi

best_profile_path=""
best_profile_mtime=0
best_root=""

profile_dirs_for_root() {
  local root="$1"
  shopt -s nullglob
  # Firefox profiles are typically under $root/*.default* or $root/*.<something>, but we'll just scan direct children.
  local dirs=( "$root"/* )
  shopt -u nullglob
  for p in "${dirs[@]}"; do
    [[ -d "$p" ]] || continue
    [[ -f "$p/prefs.js" ]] || continue
    echo "$p"
  done
}

mtime_of_profile() {
  local p="$1"
  if [[ -f "$p/prefs.js" ]]; then
    stat -c %Y "$p/prefs.js" 2>/dev/null || echo 0
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
  echo "ERROR: Found Firefox roots, but could not find any profile directories with prefs.js."
  exit 1
fi

TARGET_USER="root"
if [[ "$best_profile_path" == /home/* ]]; then
  TARGET_USER="$(echo "$best_profile_path" | awk -F/ '{print $3}')"
fi

echo "Selected (heuristic):"
echo "  Firefox binary : $FIREFOX_BIN"
echo "  Profile path   : $best_profile_path"
echo "  Target user    : $TARGET_USER"
echo
echo "NOTE: This launches Firefox with --marionette for Selenium/geckodriver 'connect existing' workflows."
echo "NOTE: Use -no-remote to ensure a separate instance. Close other Firefox instances if you hit profile lock issues."
echo

cmd=( "$FIREFOX_BIN" "-no-remote" "-profile" "$best_profile_path" "--marionette" )

if [[ "$(id -u)" -eq 0 && "$TARGET_USER" != "root" ]]; then
  if command -v runuser >/dev/null 2>&1; then
    echo "Launching as user '$TARGET_USER' via runuser..."
    exec runuser -u "$TARGET_USER" -- "${cmd[@]}"
  else
    echo "Launching as user '$TARGET_USER' via su..."
    exec su - "$TARGET_USER" -c "$(printf '%q ' "${cmd[@]}")"
  fi
else
  exec "${cmd[@]}"
fi
