"""Record the demo videos with Playwright (no manual screen capture).

Starts the Streamlit app, clicks through it like a presenter would, and
saves webui/recordings/streamlit_demo.mp4. Then does the same for the
single HTML page (html_demo.mp4). Run from projects/:
    venv/bin/python webui/record_demo.py
Needs ffmpeg for the webm -> mp4 step.
"""
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "recordings"
OUT.mkdir(exist_ok=True)
VENV = ROOT.parent / "venv" / "bin"
SIZE = {"width": 1600, "height": 900}


def pause(page, s):
    page.wait_for_timeout(int(s * 1000))


def scroll(page, px, steps=12, x=900, y=500):
    page.mouse.move(x, y)
    for _ in range(steps):
        page.mouse.wheel(0, px / steps)
        page.wait_for_timeout(60)


def pick(page, label, option):
    box = page.locator('[data-testid="stSelectbox"]').filter(has_text=label)
    box.click()
    pause(page, 0.6)
    page.get_by_role("option", name=option, exact=True).click()
    pause(page, 2.2)


def to_mp4(webm, name):
    mp4 = OUT / name
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-movflags", "+faststart", str(mp4)], check=True)
    Path(webm).unlink()
    return mp4


def record(browser, name, script):
    tmp = OUT / "_tmp"
    ctx = browser.new_context(viewport=SIZE, record_video_dir=str(tmp),
                              record_video_size=SIZE, color_scheme="light")
    page = ctx.new_page()
    script(page)
    webm = page.video.path()
    ctx.close()
    mp4 = to_mp4(webm, name)
    shutil.rmtree(tmp, ignore_errors=True)
    print("saved", mp4)


def streamlit_demo(page):
    page.goto("http://127.0.0.1:8599")
    page.get_by_text("4.1 / 4.3").wait_for(timeout=30000)
    pause(page, 3)
    # 4.3 highlight: pick a team, everyone else stays gray
    pick(page, "Highlight a team", "Red Bull")
    pick(page, "Highlight a team", "McLaren")
    # 4.1: official colors, then how a colorblind viewer sees them
    page.get_by_text("Official team colors").click()
    pause(page, 3)
    pick(page, "View as", "Deuteranopia")
    pause(page, 1.5)
    pick(page, "View as", "Normal vision")
    page.get_by_text("Top 4 + gray (Okabe-Ito)").click()
    pause(page, 1.5)
    # 4.2: three color scales on the same heatmap
    scroll(page, 620)
    pause(page, 2.5)
    page.get_by_text("Rainbow: finish position").click()
    pause(page, 3)
    page.get_by_text("Diverging: places gained").click()
    pause(page, 3)
    page.get_by_text("Sequential: finish position").click()
    pause(page, 2)
    # Lecture 5 tab
    scroll(page, -2000, steps=8)
    page.get_by_role("tab", name="Lecture 5: directory").click()
    pause(page, 3)
    pick(page, "Highlight a driver", "Oscar Piastri")
    for _ in range(4):
        scroll(page, 450)
        pause(page, 2.2)
    pause(page, 2)


def html_demo(page):
    page.goto((ROOT / "index.html").as_uri())
    page.wait_for_selector("#map .geo")
    pause(page, 2.5)
    # click three circuits on the map to show podiums
    for rnd in (1, 13, 15):
        page.evaluate(
            """r => { const el = document.getElementById('map');
                      const pt = el.data.flatMap((t, ti) =>
                        t.customdata.map((c, i) => ({c, ti, i})))
                        .find(p => p.c === r);
                      el.emit('plotly_click', {points: [{
                        customdata: r, curveNumber: pt.ti,
                        pointNumber: pt.i}]}); }""", rnd)
        pause(page, 2.2)
    scroll(page, 520, x=40)
    pause(page, 1.5)
    page.select_option("#team", "Red Bull")
    pause(page, 2)
    page.click("#official")
    pause(page, 3)
    scroll(page, 560, x=40)
    pause(page, 1.5)
    page.click("#jet")
    pause(page, 3)
    page.click("#seq")
    pause(page, 2)


if __name__ == "__main__":
    app = subprocess.Popen(
        [str(VENV / "streamlit"), "run", str(ROOT / "app.py"),
         "--server.headless", "true", "--server.port", "8599",
         "--server.address", "127.0.0.1"],
        cwd=ROOT.parent, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    try:
        time.sleep(4)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            record(browser, "streamlit_demo.mp4", streamlit_demo)
            record(browser, "html_demo.mp4", html_demo)
            browser.close()
    finally:
        app.terminate()
