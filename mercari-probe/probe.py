import json, time
from playwright.sync_api import sync_playwright

OUT = "mercari-probe/resultado.json"
URL = "https://jp.mercari.com/search?keyword=CX-5%20%E3%82%AD%E3%83%A3%E3%83%AA%E3%82%A2"
res = {"fonte": "github-actions", "url": URL, "itens": [], "total_anchors": 0}
try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chromium",
                              args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(locale="ja-JP", timezone_id="Asia/Tokyo",
                            viewport={"width": 1366, "height": 768},
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        pg = ctx.new_page()
        pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(9000)
        pg.mouse.wheel(0, 1200); pg.wait_for_timeout(3000)
        res["titulo_pagina"] = pg.title()
        res["banner_nao_suportado"] = pg.evaluate("() => (document.body.innerText||'').includes('対応していない')")
        data = pg.evaluate("""() => {
          const out = []; const seen = new Set();
          document.querySelectorAll('a[href*="/item/"]').forEach(a => {
            const href = a.getAttribute('href');
            if (!href || seen.has(href)) return; seen.add(href);
            const img = a.querySelector('img');
            const txt = (a.innerText || '').replace(/\\s+/g, ' ').trim();
            const m = txt.match(/¥\\s?[\\d,]+/);
            out.push({titulo: (img && img.getAttribute('alt')) || txt.slice(0, 80),
                      preco: m ? m[0] : '', url: href});
          });
          return out; }""")
        res["total_anchors"] = len(data)
        res["itens"] = data[:8]
        b.close()
except Exception as e:
    res["erro"] = str(e).split("\n")[0]
res["quando"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False)[:800])
