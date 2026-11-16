#!/usr/bin/env node
/**
 * Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 * File: - export_diagram_png.mjs
 * Description: Export Archify diagram HTML to Markdown-preview PNG (same stem).
 * Version: 1.0
 * Date: 2026/11/16
 * Author: limao2@Apps.Gallery
 *
 * Usage:
 *   node export_diagram_png.mjs <diagram.html> [out.png] [--chrome path]
 * Requires puppeteer (e.g. from @mermaid-js/mermaid-cli) or CHROME_PATH.
 */
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);

function loadPuppeteer() {
  const home = process.env.APPDATA || process.env.HOME || "";
  const candidates = [
    path.join(home, "npm/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer"),
    path.join(home, "npm/node_modules/puppeteer"),
    "puppeteer",
  ];
  for (const c of candidates) {
    try {
      return require(c);
    } catch {
      /* try next */
    }
  }
  throw new Error("puppeteer not found; install or set NODE_PATH");
}

function parseArgs(argv) {
  const args = { chrome: process.env.CHROME_PATH || "", html: "", out: "" };
  const rest = [];
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--chrome") {
      args.chrome = argv[++i] || "";
    } else {
      rest.push(argv[i]);
    }
  }
  args.html = rest[0] || "";
  args.out = rest[1] || "";
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (!args.html) {
  console.error("Usage: node export_diagram_png.mjs <diagram.html> [out.png] [--chrome path]");
  process.exit(2);
}

const htmlPath = path.resolve(args.html);
const outPath = path.resolve(args.out || htmlPath.replace(/\.html$/i, ".png"));
const puppeteer = loadPuppeteer();

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: args.chrome || undefined,
  args: ["--no-sandbox", "--disable-gpu", "--allow-file-access-from-files"],
});
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 1000, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(htmlPath).href, {
    waitUntil: "networkidle0",
    timeout: 90000,
  });
  await page.waitForSelector("svg[data-quality-profile]", { timeout: 30000 });
  const clip = await page.evaluate(() => {
    const svg = document.querySelector("svg[data-quality-profile]");
    const r = svg.getBoundingClientRect();
    return {
      x: Math.max(0, Math.floor(r.x - 20)),
      y: Math.max(0, Math.floor(r.y - 20)),
      width: Math.ceil(r.width + 40),
      height: Math.ceil(r.height + 40),
    };
  });
  await page.screenshot({ path: outPath, clip, type: "png" });
  console.log(outPath, fs.statSync(outPath).size);
} finally {
  await browser.close();
}
