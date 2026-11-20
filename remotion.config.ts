import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
Config.setOverwriteOutput(true);
Config.setConcurrency(4);
// Di cloud container pakai Chromium bawaan; di PC biasa baris ini otomatis diabaikan bila file tidak ada.
const fs = require("fs");
const shell = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
if (fs.existsSync(shell)) Config.setBrowserExecutable(shell);
