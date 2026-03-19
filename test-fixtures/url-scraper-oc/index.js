#!/usr/bin/env node
import { ProxyAgent, setGlobalDispatcher } from 'undici';

const proxy = process.env.https_proxy || process.env.HTTPS_PROXY || process.env.http_proxy || process.env.HTTP_PROXY;
if (proxy) setGlobalDispatcher(new ProxyAgent(proxy));

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h') || !args.length) {
  console.log(`url-scraper — 抓取页面 title 和 meta description

用法: url-scraper <URL>

选项:
  --help, -h  显示帮助

示例:
  url-scraper https://example.com`);
  process.exit(0);
}

const url = args[0];
if (!/^https?:\/\//i.test(url)) {
  console.error(JSON.stringify({ error: 'URL 必须以 http:// 或 https:// 开头' }));
  process.exit(1);
}

try {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'url-scraper/1.0' },
    signal: AbortSignal.timeout(15000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const html = await res.text();
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.trim() || null;
  const desc = (html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([\s\S]*?)["']/i)
    || html.match(/<meta[^>]*content=["']([\s\S]*?)["'][^>]*name=["']description["']/i))?.[1]?.trim() || null;
  console.log(JSON.stringify({ url, title, description: desc }, null, 2));
} catch (e) {
  console.error(JSON.stringify({ url, error: e.message }, null, 2));
  process.exit(1);
}
