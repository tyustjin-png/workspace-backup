#!/usr/bin/env node

import { ProxyAgent, setGlobalDispatcher } from 'undici';

// 自动检测代理
const proxy = process.env.https_proxy || process.env.HTTPS_PROXY || process.env.http_proxy || process.env.HTTP_PROXY;
if (proxy) {
  setGlobalDispatcher(new ProxyAgent(proxy));
}

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h') || args.length === 0) {
  console.log(`
url-scraper - 抓取页面 title 和 meta description

用法:
  url-scraper <URL>
  url-scraper --help

参数:
  URL       要抓取的页面地址（需包含 http:// 或 https://）

示例:
  url-scraper https://example.com
  url-scraper https://github.com
`);
  process.exit(0);
}

const url = args[0];

if (!/^https?:\/\//i.test(url)) {
  console.error(JSON.stringify({ error: "URL 必须以 http:// 或 https:// 开头" }, null, 2));
  process.exit(1);
}

async function scrape(url) {
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'url-scraper/1.0' },
      signal: AbortSignal.timeout(10000)
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    const html = await res.text();

    const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
    const title = titleMatch ? titleMatch[1].trim() : null;

    const descMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([\s\S]*?)["'][^>]*>/i)
      || html.match(/<meta[^>]*content=["']([\s\S]*?)["'][^>]*name=["']description["'][^>]*>/i);
    const description = descMatch ? descMatch[1].trim() : null;

    console.log(JSON.stringify({ url, title, description }, null, 2));
  } catch (err) {
    console.error(JSON.stringify({ url, error: err.message }, null, 2));
    process.exit(1);
  }
}

scrape(url);
