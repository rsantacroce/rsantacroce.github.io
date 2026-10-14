#!/usr/bin/env python3
"""Build index.html (GitHub Pages) and ../rsantacroce/README.md (profile) from projects.json.

To hide a project, delete its entry from projects.json and run: python3 build.py
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE_URL = "https://rsantacroce.github.io"
PROFILE_README = ROOT.parent / "rsantacroce" / "README.md"

data = json.loads((ROOT / "projects.json").read_text())
profile, sections = data["profile"], data["sections"]


def gh(repo):
    return f"https://github.com/{repo}"


def card(p):
    private = p.get("private", False)
    # Private repos link to their public site if they have one, otherwise nothing.
    main = p.get("url") or p.get("pages") or (None if private else gh(p["repo"]))
    title = escape(p["name"])
    title = f'<a href="{escape(main)}">{title}</a>' if main else title
    links = []
    if p.get("repo") and not private:
        links.append(f'<a href="{gh(p["repo"])}">{escape(p["repo"])}</a>')
    # Public repo holding the project's GitHub Pages site.
    if p.get("site_repo"):
        links.append(f'<a href="{gh(p["site_repo"])}">{escape(p["site_repo"])}</a>')
    for u in dict.fromkeys(filter(None, [p.get("url"), p.get("pages")])):
        host = u.split("//", 1)[1].rstrip("/")
        links.append(f'<a href="{escape(u)}">{escape(host)}</a>')
    meta = []
    if p.get("lang"):
        meta.append(f'<span class="lang">{escape(p["lang"])}</span>')
    if private:
        meta.append('<span class="private" title="Private repository">Private</span>')
    search = escape(" ".join([p["name"], p["desc"], p.get("lang", ""), p.get("repo", "")]).lower())
    return f"""      <article class="card" data-search="{search}">
        <h3>{title}</h3>
        <p>{escape(p["desc"])}</p>
        <div class="meta">{"".join(meta)}</div>
        {f'<div class="links">{" · ".join(links)}</div>' if links else ""}
      </article>"""


def build_html():
    total = sum(len(s["projects"]) for s in sections)
    nav = "".join(f'<a href="#{s["id"]}">{escape(s["title"])}</a>' for s in sections)
    bio = "".join(f"<p>{escape(b)}</p>" for b in profile["bio"])
    links = "".join(f'<a href="{escape(l["url"])}">{escape(l["label"])}</a>' for l in profile["links"])
    body = "\n".join(
        f"""    <section id="{s["id"]}">
      <h2>{escape(s["title"])} <span class="count">{len(s["projects"])}</span></h2>
      <p class="intro">{escape(s["intro"])}</p>
      <div class="grid">
{chr(10).join(card(p) for p in s["projects"])}
      </div>
    </section>"""
        for s in sections
    )
    template = (ROOT / "template.html").read_text()
    return (
        template.replace("{{NAME}}", escape(profile["name"]))
        .replace("{{TAGLINE}}", escape(profile["tagline"]))
        .replace("{{BIO}}", bio)
        .replace("{{LINKS}}", links)
        .replace("{{NAV}}", nav)
        .replace("{{TOTAL}}", str(total))
        .replace("{{SECTIONS}}", body)
    )


def build_readme():
    out = [f"# Hi, I'm {profile['name']}", "", f"**{profile['tagline']}**", ""]
    out += [profile["bio"][0], "", profile["bio"][1], ""]
    out += [" · ".join(f"[{l['label']}]({l['url']})" for l in profile["links"]), ""]
    out += [f"### 👉 [See all my projects]({PAGE_URL})", ""]
    out += ["### Highlights", ""]
    for s in sections:
        public = [p for p in s["projects"] if not p.get("private") or p.get("url")][:4]
        items = []
        for p in public:
            link = p.get("url") or p.get("pages") or gh(p["repo"])
            items.append(f"[{p['name']}]({link})")
        out.append(f"- **{s['title']}**: {', '.join(items)}")
    out += ["", f"More, with descriptions, at **[{PAGE_URL.split('//')[1]}]({PAGE_URL})**.", ""]
    return "\n".join(out)


(ROOT / "index.html").write_text(build_html())
print("wrote", ROOT / "index.html")
PROFILE_README.parent.mkdir(exist_ok=True)
PROFILE_README.write_text(build_readme())
print("wrote", PROFILE_README)
