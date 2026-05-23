const fs = require("fs");

const html = fs.readFileSync("index.html", "utf8");

const required = [
  "<!doctype html>",
  '<html lang="ja">',
  'id="title"',
  'id="output"',
  'data-output="gem"',
  'href="docs/',
];

const missing = required.filter((text) => !html.includes(text));
if (missing.length) {
  console.error(`Missing expected content: ${missing.join(", ")}`);
  process.exit(1);
}

const openingScriptTags = html.match(/<script\b/g) ?? [];
const closingScriptTags = html.match(/<\/script>/g) ?? [];
if (openingScriptTags.length !== closingScriptTags.length) {
  console.error("Script tag count does not match.");
  process.exit(1);
}

console.log("STATIC_APP_OK");
