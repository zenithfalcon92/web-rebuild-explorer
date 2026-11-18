import asyncio
import json
import sys
from playwright.async_api import async_playwright

async def explore(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto(url, wait_until='networkidle', timeout=30000)
        title = await page.title()
        links = await page.eval_on_selector_all('a', 'els => els.map(e => ({text: e.innerText.trim(), href: e.href})).filter(x => x.text && x.href)')
        buttons = await page.eval_on_selector_all('button', 'els => els.map(e => e.innerText.trim()).filter(Boolean)')
        forms = await page.eval_on_selector_all('form', 'els => els.map(e => ({action: e.action, method: e.method}))')
        headings = await page.eval_on_selector_all('h1,h2,h3', 'els => els.map(e => ({tag: e.tagName.toLowerCase(), text: e.innerText.trim()}))')
        images = await page.eval_on_selector_all('img', 'els => els.map(e => ({src: e.src, alt: e.alt})).slice(0, 20)')
        await page.screenshot(path='page.png', full_page=True)
        await browser.close()
        return {
            'url': url,
            'title': title,
            'headings': headings[:20],
            'links': links[:30],
            'buttons': buttons[:20],
            'forms': forms[:10],
            'images': images,
        }

def build_checklist(data):
    checklist = []
    if not data['title']:
        checklist.append('Add a page title')
    if not data['headings']:
        checklist.append('Add semantic headings')
    if not data['links']:
        checklist.append('Add navigation links')
    if not data['images']:
        checklist.append('Check visual assets')
    else:
        missing_alt = [img for img in data['images'] if not img.get('alt')]
        if missing_alt:
            checklist.append('Add alt text to %d image(s)' % len(missing_alt))
    return checklist

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
    data = asyncio.run(explore(target))
    data['reconstruction_checklist'] = build_checklist(data)
    with open('site_profile.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Saved site_profile.json and page.png')
    print('Title:', data['title'])
    print('Links:', len(data['links']), 'Buttons:', len(data['buttons']), 'Forms:', len(data['forms']))

if __name__ == '__main__':
    main()