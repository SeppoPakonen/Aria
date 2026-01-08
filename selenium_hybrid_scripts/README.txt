Selenium Hybrid Browser Launcher Scripts (Heuristic Profile Picker)
==============================================================

What this is
------------
These scripts launch a browser in a way that supports "hybrid" workflows:
- the user can interact normally (log in, solve captchas, do 2FA)
- automation can attach later (e.g., Selenium via Chrome DevTools/remote debugging for Chromium/Chrome,
  or via geckodriver connect-existing for Firefox)

Important warning
-----------------
Each script chooses a profile using a HEURISTIC: it picks the profile directory whose key file
(Chromium/Chrome: Preferences, Firefox: prefs.js) has the newest modification time.

Heuristics can be wrong. If you have multiple users and multiple profiles, it might pick the wrong one.

Files
-----
Linux:
  - linux_chromium_debug.sh   (Chromium/Chrome with --remote-debugging-port)
  - linux_firefox_marionette.sh (Firefox with --marionette)

Windows:
  - windows_chrome_debug.bat
  - windows_firefox_marionette.bat

Usage
-----
Linux (run as root or normal user):
  chmod +x linux_chromium_debug.sh linux_firefox_marionette.sh
  ./linux_chromium_debug.sh
  ./linux_firefox_marionette.sh

Optional env vars:
  PORT=9222                       (Chromium/Chrome debug port)
  CHROME_BIN=chromium             (override browser binary)
  FIREFOX_BIN=firefox             (override Firefox binary)
  EXTRA_CHROME_FLAGS="--no-sandbox" (only if you must run Chromium as root)

Windows:
  Double-click the .bat files in Explorer or run from cmd.exe:
    windows_chrome_debug.bat
    windows_firefox_marionette.bat

Optional env var:
  PORT=9222 (Chrome debug port)

Notes
-----
- Close other browser instances that use the same profile, otherwise you can hit profile lock issues.
- For Linux: the scripts scan /home/* and /root to heuristically pick the most active user/profile and, if run as root,
  they attempt to launch the browser as that target user (runuser/su) to avoid running browsers as root.
