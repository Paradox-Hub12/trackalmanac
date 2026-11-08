// Site check: opens every page of the built site in a real browser and reports problems.
//
//   npm i --no-save playwright@1.47.2 && npx playwright install chromium     (once)
//   python3 build.py
//   node scripts/site_check.mjs                         every page, 5 widths, dark and light
//   node scripts/site_check.mjs / /championship/        only these pages
//   node scripts/site_check.mjs --quick                 every page at 390px (dark) and 1366px (light)
//
// For each page it checks: no JavaScript errors, nothing wider than the screen (no sideways scrolling), and that
// the page has a <title> and an <h1>/<h2>. Google Fonts, Analytics and Firebase are blocked during the check
// (an offline font can make a heading slightly wider, so a heading that only just overflows may be a false alarm).
// Exit code 1 if anything failed. Set CHROMIUM_PATH to use a browser that is already installed.
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PORT = 8790 + Math.floor(Math.random() * 100);
const args = process.argv.slice(2);
const quick = args.includes("--quick");
let pages = args.filter(a => a.startsWith("/"));
if (!pages.length) {
  const sm = readFileSync(path.join(ROOT, "sitemap.xml"), "utf8");
  pages = [...sm.matchAll(/<loc>https?:\/\/[^/]+(\/[^<]*)<\/loc>/g)].map(m => m[1]);
  pages.push("/game/picks/", "/game/account/", "/game/leagues/", "/404.html");
}
const combos = quick ? [[390, "dark"], [1366, "light"]] : [[320, "dark"], [390, "light"], [820, "dark"], [1024, "light"], [1366, "dark"]];

const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
let failures = 0;
try {
  for (const [w, theme] of combos) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
    await ctx.addInitScript(t => { try { localStorage.setItem("ta-theme", t); localStorage.setItem("ta-consent", "essential"); localStorage.setItem("ta-firstnote", "1"); } catch (e) {} }, theme);
    await ctx.route(/googleapis|gstatic|googletagmanager|firebase/, r => r.abort());
    let bad = 0;
    for (const u of pages) {
      const p = await ctx.newPage(); const errs = [];
      p.on("pageerror", e => errs.push(e.message));
      try { await p.goto(`http://127.0.0.1:${PORT}${u}`, { waitUntil: "load", timeout: 20000 }); await p.waitForTimeout(400); }
      catch (e) { errs.push("could not load: " + e.message.split("\n")[0]); }
      const r = await p.evaluate(() => {
        const W = document.documentElement.clientWidth, off = [];
        document.querySelectorAll("body *").forEach(el => {
          const cs = getComputedStyle(el); if (cs.display === "none" || cs.visibility === "hidden" || cs.position === "fixed") return;
          const b = el.getBoundingClientRect(); if (!b.width || b.right <= W + 1) return;
          for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) if (/(auto|scroll|hidden|clip)/.test(getComputedStyle(a).overflowX)) return;
          off.push(`${el.tagName.toLowerCase()}.${String(el.className).split(" ")[0]} (right edge ${Math.round(b.right)}px)`);
        });
        return { wide: document.documentElement.scrollWidth > W ? document.documentElement.scrollWidth : 0, off: off.slice(0, 3),
                 title: !!document.title, heading: !!document.querySelector("h1,h2") };
      }).catch(e => ({ wide: 0, off: [], title: false, heading: false, err: e.message }));
      const problems = [...errs.map(e => "JS error: " + e)];
      if (r.wide) problems.push(`page is ${r.wide}px wide: ${r.off.join(", ") || "unknown element"}`);
      else if (r.off.length) problems.push("element wider than the screen: " + r.off.join(", "));
      if (!r.title) problems.push("no <title>");
      if (!r.heading && u !== "/404.html") problems.push("no heading");
      if (problems.length) { bad++; failures++; console.log(`✗ ${w}px ${theme} ${u}\n    ${problems.join("\n    ")}`); }
      await p.close();
    }
    console.log(`${bad ? "✗" : "✓"} ${w}px ${theme}: ${pages.length - bad}/${pages.length} pages OK`);
    await ctx.close();
  }
} finally { await browser.close(); server.kill(); }
process.exit(failures ? 1 : 0);
