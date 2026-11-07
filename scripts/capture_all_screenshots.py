import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.abspath('demo/assets/screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

TARGETS = [
    ('01-dashboard.png', 'Dashboard', 'Active Tenders'),
    ('02-switch-war-room.png', 'Switch War Room', 'Switch War Room'),
    ('03-tender-analysis.png', 'Tender Analysis', 'Tender Analysis & Clause Extraction'),
    ('04-compliance-matrix.png', 'Compliance Center', 'Compliance Center & Matrix Evaluation'),
    ('05-prooflink.png', 'ProofLink Traceability', 'ProofLink Traceability Engine'),
    ('06-evidence-research.png', 'Evidence Library', 'Evidence Library & Proof Vault'),
    ('07-proposal-generation.png', 'Proposal Studio', 'Proposal Studio & Drafting Workspace'),
    ('08-bid-audit.png', 'Independent Bid Audit', 'Independent Bid Audit & Risk Verification'),
    ('09-human-approval.png', 'Human Approval Gate', 'Human-in-the-Loop Approval Gate'),
    ('10-final-deliverables.png', 'Final Deliverables', 'Final Deliverables & Export Bundle'),
]

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            color_scheme='dark',
        )
        page = context.new_page()

        print("1. Navigating to http://localhost:3000/ ...")
        page.goto('http://localhost:3000/', wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Check if login screen is presented
        is_login = page.evaluate('() => !document.querySelector("header")')
        if is_login:
            print("2. Authenticating as Administrator via demo profile...")
            clicked_admin = page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const adminBtn = btns.find(b => b.textContent && b.textContent.includes('Administrator'));
                if (adminBtn) {
                    adminBtn.click();
                    return true;
                }
                return false;
            }''')
            if clicked_admin:
                print("Clicked Administrator login button. Waiting for dashboard...")
                page.wait_for_timeout(2000)
            else:
                print("Warning: Administrator login button not found, trying form fill...")
                page.fill('input[type="email"]', 'admin@tenderforge.com')
                page.fill('input[type="password"]', 'TenderForgeAdmin2026!')
                page.click('button[type="submit"]')
                page.wait_for_timeout(2000)

        print("3. Capturing all 10 views in 1920x1080 (16:9)...")
        for filename, nav_text, expected_heading in TARGETS:
            out_path = os.path.join(SCREENSHOTS_DIR, filename)

            # Click navigation item
            switched = page.evaluate('''(btnText) => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const btn = buttons.find(b => {
                    const t = b.textContent ? b.textContent.trim() : '';
                    return t === btnText || t.startsWith(btnText) || t.includes(btnText);
                });
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            }''', nav_text)

            if not switched:
                print(f"Warning: Could not find button '{nav_text}'")

            # Wait for content to render smoothly
            page.wait_for_timeout(1200)

            # Capture high-quality screenshot
            page.screenshot(path=out_path)
            size_kb = os.path.getsize(out_path) / 1024
            print(f"-> Captured {filename} ({size_kb:.1f} KB) for '{nav_text}'")

        browser.close()
    print("All 10 official screenshots captured and updated successfully!")

if __name__ == '__main__':
    capture_all()
