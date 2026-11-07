"""
cricbuzz_score.py
-----------------
Opens Cricbuzz in a real browser (Playwright), waits for the live score
element to appear, prints the score and saves a screenshot as score.png.

Setup (inside your venv):
    pip install playwright
    playwright install chromium

Run:
    python cricbuzz_score.py              # headed  - you watch the browser
    python cricbuzz_score.py --headless   # headless - no window, runs in background
"""

import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

# ------------------------------- settings ------------------------------------
URL = "https://www.cricbuzz.com/"

# Paste the selector YOU found with right-click > Inspect on the score.
# Test it first in Chrome's console:  document.querySelector("your-selector")
# Examples of the format:  ".some-class"   "div.some-class"   "#some-id"
SELECTOR = "div.bg-white.flex.justify-between.items-center.px-4.py-2"

# Only pick the match whose score box contains this text (team short name).
# Examples: "IND", "AUS", "CSK".  Leave "" to take the first match on the page.
TEAM_FILTER = "IND"

WAIT_SECONDS = 20       # max time to wait for the score before giving up
MAX_SCORES = 1          # print only one match
SCREENSHOT = "score.png"

HEADLESS = "--headless" in sys.argv


def main() -> None:
    if not SELECTOR:
        sys.exit("Set SELECTOR at the top of the file first "
                 "(right-click the score on Cricbuzz > Inspect).")

    mode = "headless" if HEADLESS else "headed"
    print(f"Opening Cricbuzz ({mode})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page(viewport={"width": 1366, "height": 900})

        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=30_000)

            # Wait for the score element itself - no fixed sleep.
            scores = page.locator(SELECTOR)
            if TEAM_FILTER:
                scores = scores.filter(has_text=TEAM_FILTER)
                print(f"Looking for a live match with '{TEAM_FILTER}'...")
            scores.first.wait_for(state="visible", timeout=WAIT_SECONDS * 1000)

            texts = [t.strip() for t in scores.all_inner_texts() if t.strip()]
            print()
            for text in texts[:MAX_SCORES]:
                print(text)
                print("-" * 40)

        except PlaywrightTimeout:
            # The score never appeared: no live match right now, or the selector changed.
            target = f" for '{TEAM_FILTER}'" if TEAM_FILTER else ""
            print(f"\nNo live score found{target} within {WAIT_SECONDS}s.")
            print("Either no match is live right now, or Cricbuzz changed its page -")
            print("re-check the selector with Inspect.")

        finally:
            page.screenshot(path=SCREENSHOT)   # saved either way, useful for debugging
            print(f"\nsaved {SCREENSHOT}")
            browser.close()


if __name__ == "__main__":
    main()