#!/usr/bin/env node
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - export_diagram_png.mjs
 ** Description: Export Archify diagram HTML to Markdown-preview PNG (same stem).
 ** Version: 1.1
 ** Date: 2026/11/16
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/16 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/16 1.1 截图前隐藏查看器浮动 UI（toolbar/diagram-nav 等，
 **                                   复用 Archify print 隐藏规则）；导出成功后把
 **                                   finalize/browser-check/delivery 等证据 JSON 移入
 **                                   仓库根 .archify/evidence/，diagrams/ 只留 html+png
 *********************************************************************************/
/**
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

// 从 start 目录向上找 git 仓库根；找不到返回 null
function findGitRoot(start) {
  let cur = path.resolve(start);
  for (;;) {
    try {
      if (fs.existsSync(path.join(cur, ".git"))) return cur;
    } catch {
      /* ignore */
    }
    const parent = path.dirname(cur);
    if (parent === cur) return null;
    cur = parent;
  }
}

// 把 Archify 生成的证据 JSON（finalize / browser-check / delivery 等）移出 diagrams/，
// 统一收进仓库根 .archify/evidence/，交付目录只保留 html + png。
function moveEvidenceFiles(htmlPath) {
  const dir = path.dirname(htmlPath);
  const stemLower = path.basename(htmlPath, ".html").toLowerCase();
  const gitRoot = findGitRoot(dir);
  if (!gitRoot) return [];
  const evidenceDir = path.join(gitRoot, ".archify", "evidence");
  const suffixes = [
    "browser-check.json",
    "delivery.json",
    "finalize.json",
    "finalize-summary.json",
  ];
  const moved = [];
  for (const f of fs.readdirSync(dir)) {
    const fl = f.toLowerCase();
    if (suffixes.some((s) => fl === `${stemLower}.${s}`)) {
      fs.mkdirSync(evidenceDir, { recursive: true });
      const dest = path.join(evidenceDir, f);
      fs.renameSync(path.join(dir, f), dest);
      moved.push(dest);
    }
  }
  return moved;
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
  // 截图前隐藏查看器浮动 UI（对齐 Archify 自带 print 隐藏规则），避免 ROUTE/LENS 工具条入图
  await page.addStyleTag({
    content:
      ".toolbar, .diagram-nav, .focus-chip, .archify-toast, .no-print { display: none !important; }",
  });
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
  const moved = moveEvidenceFiles(htmlPath);
  if (moved.length) {
    console.log(`evidence moved to .archify/evidence/: ${moved.length} file(s)`);
  }
} finally {
  await browser.close();
}
