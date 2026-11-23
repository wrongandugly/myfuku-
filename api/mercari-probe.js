const chromium = require('@sparticuz/chromium');
const { chromium: pw } = require('playwright-core');

module.exports = async (req, res) => {
  const q = (req.query && req.query.q) || 'CX-5 キャリア';
  let browser = null;
  try {
    browser = await pw.launch({
      args: chromium.args,
      executablePath: await chromium.executablePath(),
      headless: true,
    });
    const ctx = await browser.newContext({
      locale: 'ja-JP',
      timezoneId: 'Asia/Tokyo',
      viewport: { width: 1366, height: 768 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    });
    const pg = await ctx.newPage();
    await pg.goto('https://jp.mercari.com/search?keyword=' + encodeURIComponent(q),
      { waitUntil: 'domcontentloaded', timeout: 45000 });
    await pg.waitForTimeout(8000);
    await pg.mouse.wheel(0, 1200);
    await pg.waitForTimeout(2500);
    const items = await pg.evaluate(() => {
      const out = []; const seen = new Set();
      document.querySelectorAll('a[href*="/item/"]').forEach(a => {
        const h = a.getAttribute('href');
        if (!h || seen.has(h)) return; seen.add(h);
        const img = a.querySelector('img');
        const txt = (a.innerText || '').replace(/\s+/g, ' ').trim();
        const m = txt.match(/¥\s?[\d,]+/);
        out.push({ titulo: (img && img.getAttribute('alt')) || txt.slice(0, 80),
                   preco: m ? m[0] : '', url: h });
      });
      return out;
    });
    res.status(200).json({ total: items.length, itens: items.slice(0, 8), titulo_pagina: await pg.title() });
  } catch (e) {
    res.status(200).json({ total: 0, erro: String(e).split('\n')[0] });
  } finally {
    if (browser) await browser.close();
  }
};
