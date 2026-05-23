const fs = require("fs");

const html = fs.readFileSync("index.html", "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);

for (const script of scripts) {
  new Function(script);
}

const required = [
  "学校マネジメント相談カード作成アプリ",
  'id="title"',
  'id="output"',
  'data-output="gem"',
  "Gem学校マネジメント相談室_使い方マニュアル.html",
];

const missing = required.filter((text) => !html.includes(text));
if (missing.length) {
  console.error(`Missing expected content: ${missing.join(", ")}`);
  process.exit(1);
}

console.log("STATIC_APP_OK");
