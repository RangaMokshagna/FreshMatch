"""Render generated slide HTML to PDF and PNG previews using local Chromium."""
from pathlib import Path
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
with sync_playwright() as p:
    executable=shutil.which('chromium') or shutil.which('google-chrome')
    if not executable:raise SystemExit('Chromium is required for preview rendering.')
    browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
    page.set_content((ROOT/'FreshMatch_Presentation_Preview.html').read_text(),wait_until='load')
    count=page.locator('.slide').count()
    assert count==10
    for i in range(count):page.locator('.slide').nth(i).screenshot(path=str(ROOT/'preview'/f'slide-{i+1:02d}.png'))
    page.pdf(path=str(ROOT/'FreshMatch_Project_Presentation.pdf'),print_background=True,prefer_css_page_size=True)
    browser.close()
sheet=Image.new('RGB',(1280,1800),'#dce4dc')
for i in range(10):
    image=Image.open(ROOT/'preview'/f'slide-{i+1:02d}.png').convert('RGB')
    image.thumbnail((640,360));sheet.paste(image,((i%2)*640,(i//2)*360))
sheet.save(ROOT/'FreshMatch_Slides_Overview.png')
print('Rendered 10 slides and PDF.')
