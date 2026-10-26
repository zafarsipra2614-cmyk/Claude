import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
// use the Chromium already installed in this container instead of downloading one
Config.setBrowserExecutable('/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
