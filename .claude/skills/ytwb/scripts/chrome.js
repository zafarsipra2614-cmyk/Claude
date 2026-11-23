// Shared Chrome lookup. CHROME_PATH wins; running as root (containers) needs --no-sandbox, added by callers.
const fs = require("fs");
exports.findChrome = function () {
  const c = [process.env.CHROME_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/opt/pw-browsers/chromium",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"].filter(Boolean);
  const hit = c.find(p => fs.existsSync(p));
  if (!hit) { console.error("Chrome not found. Set CHROME_PATH=/path/to/chrome"); process.exit(1); }
  return hit;
};
