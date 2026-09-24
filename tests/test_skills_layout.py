import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server


VIEWPORTS = [
    {"width": 320, "height": 568},
    {"width": 768, "height": 600},
    {"width": 1024, "height": 768},
    {"width": 1440, "height": 900},
]


def _browser_executable():
    configured = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    candidates = [
        configured,
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((path for path in candidates if path and Path(path).is_file()), None)


def test_skills_content_does_not_overlap_about_section(app, monkeypatch):
    import data

    monkeypatch.setattr(
        data,
        "skill_list",
        [
            {
                "name": f"Skill {index}",
                "type": "technical" if index % 2 else "soft",
                "details": "A representative skill description.",
            }
            for index in range(15)
        ],
    )

    server = make_server("127.0.0.1", 0, app)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        with sync_playwright() as playwright:
            launch_options = {"headless": True}
            executable = _browser_executable()
            if executable:
                launch_options["executable_path"] = executable
            browser = playwright.chromium.launch(**launch_options)

            try:
                for viewport in VIEWPORTS:
                    page = browser.new_page(viewport=viewport)
                    page.goto(
                        f"http://127.0.0.1:{server.server_port}/",
                        wait_until="domcontentloaded",
                    )

                    bounds = page.evaluate(
                        """
                        () => {
                          const skills = document.querySelector("#skills");
                          const about = document.querySelector("#about");
                          const visibleDescendants = [...skills.querySelectorAll("*")]
                            .filter((element) => getComputedStyle(element).display !== "none")
                            .map((element) => {
                              const rect = element.getBoundingClientRect();
                              let parent = element.parentElement;
                              let bottom = rect.bottom;
                              while (parent && parent !== skills) {
                                const style = getComputedStyle(parent);
                                if (/(auto|hidden|scroll)/.test(style.overflowY)) {
                                  bottom = Math.min(bottom, parent.getBoundingClientRect().bottom);
                                }
                                parent = parent.parentElement;
                              }
                              return bottom;
                            });

                          return {
                            skillsContentBottom: Math.max(
                              skills.getBoundingClientRect().top,
                              ...visibleDescendants,
                            ),
                            aboutTop: about.getBoundingClientRect().top,
                          };
                        }
                        """
                    )
                    page.close()

                    overlap = bounds["skillsContentBottom"] - bounds["aboutTop"]
                    assert overlap <= 1, (
                        f"Skills overlap About by {overlap:.1f}px at "
                        f"{viewport['width']}x{viewport['height']}"
                    )
            finally:
                browser.close()
    finally:
        server.shutdown()
        server_thread.join(timeout=5)


def test_mobile_skills_max_length_and_scroll(app, monkeypatch):
    import data

    monkeypatch.setattr(
        data,
        "skill_list",
        [
            {
                "name": f"Skill {index}",
                "type": "technical" if index % 2 else "soft",
                "details": "A representative skill description.",
            }
            for index in range(15)
        ],
    )

    mobile_viewports = [
        {"width": 320, "height": 568},
        {"width": 375, "height": 667},
        {"width": 414, "height": 896},
    ]

    server = make_server("127.0.0.1", 0, app)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        with sync_playwright() as playwright:
            launch_options = {"headless": True}
            executable = _browser_executable()
            if executable:
                launch_options["executable_path"] = executable
            browser = playwright.chromium.launch(**launch_options)

            try:
                for viewport in mobile_viewports:
                    page = browser.new_page(viewport=viewport)
                    page.goto(
                        f"http://127.0.0.1:{server.server_port}/",
                        wait_until="domcontentloaded",
                    )

                    result = page.evaluate(
                        """
                        () => {
                          const skillsSection = document.querySelector("#skills");
                          const container = document.querySelector(".skills-container");
                          const cards = [...document.querySelectorAll(".skill-card")];
                          const cRect = container.getBoundingClientRect();

                          const initialVisibleCards = cards.filter((card) => {
                            const r = card.getBoundingClientRect();
                            return r.bottom <= cRect.bottom + 2 && r.top >= cRect.top - 2;
                          });

                          // Scroll down to verify rest of skills become accessible
                          container.scrollTop = 400;
                          const lastCard = cards[cards.length - 1];
                          const rLast = lastCard.getBoundingClientRect();
                          const lastCardVisibleAfterScroll = (rLast.bottom <= cRect.bottom + 2 && rLast.top >= cRect.top - 2);

                          return {
                            skillsHeight: skillsSection.offsetHeight,
                            containerHeight: container.offsetHeight,
                            scrollHeight: container.scrollHeight,
                            clientHeight: container.clientHeight,
                            totalCards: cards.length,
                            initialVisibleCount: initialVisibleCards.length,
                            lastCardVisibleAfterScroll: lastCardVisibleAfterScroll,
                          };
                        }
                        """
                    )
                    page.close()

                    assert result["totalCards"] >= 15, "Expected at least 15 skills to test scrolling"
                    assert 550 <= result["clientHeight"] <= 610, (
                        f"Expected container height around ~590px (5-6 skills height) on mobile, got {result['clientHeight']}"
                    )
                    assert result["initialVisibleCount"] >= 8, (
                        f"Expected around 8-10 skills visible initially on mobile ({viewport['width']}x{viewport['height']}), "
                        f"got {result['initialVisibleCount']}"
                    )
                    assert result["scrollHeight"] > result["clientHeight"], (
                        f"Skills container should be vertically scrollable on mobile ({viewport['width']}x{viewport['height']})"
                    )
                    assert result["lastCardVisibleAfterScroll"] is True, (
                        f"Skills beyond the initial view should become visible when scrolled ({viewport['width']}x{viewport['height']})"
                    )
                    assert result["skillsHeight"] >= 800, (
                        f"Skills section should match the height scale of other sections (>=800px): {result['skillsHeight']}px"
                    )
                    assert result["skillsHeight"] <= 1000, (
                        f"Skills section max length exceeded: {result['skillsHeight']}px at {viewport['width']}x{viewport['height']}"
                    )
            finally:
                browser.close()
    finally:
        server.shutdown()
        server_thread.join(timeout=5)
