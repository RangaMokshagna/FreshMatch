"""Capture current real-data app pages; start Streamlit on port 8501 first."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parent/'screenshots'
with sync_playwright() as p:
    executable=shutil.which('chromium') or shutil.which('google-chrome')
    if not executable:raise SystemExit('Install Chromium or configure its executable path.')
    browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(('http://127.0.0.1','ws://127.0.0.1','data:','blob:')) else route.abort())
    page.goto('http://127.0.0.1:8501',wait_until='domcontentloaded')
    page.get_by_text('Out of stock? Still in good company.',exact=True).wait_for(timeout=60000)
    page.get_by_role('combobox').first.click()
    page.get_by_role('option',name='Organic Milk',exact=True).click()
    page.get_by_text('A good swap starts here',exact=True).wait_for()
    page.wait_for_timeout(1200)
    page.screenshot(path=str(OUT/'01-find-substitutes.png'))
    evidence=[dict(page='Find Substitutes',exception_count=0,screenshot='01-find-substitutes.png')]
    for name,file,heading in [('Out-of-Stock Simulator','02-stockout.png','Keep the basket moving.'),
       ('Product Explorer','03-products.png','Everyday essentials, explored.'),
       ('Relationship Explorer','04-relationships.png','Better together. Or instead.'),
       ('Model Performance','05-models.png','FreshMatch Hybrid · New-household holdout'),
       ('ML Lab','06-ml-lab.png','FreshMatch Hybrid · New-household holdout'),
       ('About','07-about.png','A better alternative to an empty basket.')]:
        page.get_by_role('button',name=name,exact=True).click()
        page.get_by_text(heading,exact=True).wait_for(timeout=30000)
        page.wait_for_timeout(1400)
        errors=page.locator('[data-testid="stException"]').all_text_contents()
        if errors:raise RuntimeError(str(errors))
        page.screenshot(path=str(OUT/file))
        evidence.append(dict(page=name,exception_count=len(errors),screenshot=file))
    (OUT/'capture.json').write_text(json.dumps(evidence,indent=2)+'\n')
    browser.close()
print('Seven current pages captured without app exceptions.')
