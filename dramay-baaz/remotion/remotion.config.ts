import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
// use the Chromium already installed in this container instead of downloading one
Config.setBrowserExecutable('/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
// software WebGL2 (SwiftShader via ANGLE): needed for three.js, effects and shader transitions in this headless container
Config.setChromiumOpenGlRenderer('swangle');
