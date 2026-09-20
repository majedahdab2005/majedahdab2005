#!/usr/bin/env python3
"""Build assets/metrics.svg from the GitHub GraphQL API.

Runs inside GitHub Actions (see .github/workflows/metrics.yml) so the profile
never depends on a third party service being up. No pip installs needed.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

BG, PANEL, LINE, LINE_2 = "#05080A", "#0A100C", "#12291C", "#1C4A2E"
G_DEEP, G_MAIN, G_BRIGHT = "#0E8F3C", "#1BE45C", "#4DFF8A"
TXT, DIM, DIM_2 = "#DCEFE2", "#6E8C79", "#48604F"
MONO = ("ui-monospace,'JetBrains Mono','SFMono-Regular',Menlo,Consolas,"
        "'Liberation Mono',monospace")

QUERY = """
query($login:String!){
  user(login:$login){
    followers{ totalCount }
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      contributionCalendar{ totalContributions }
    }
    repositories(first:100, isFork:false, ownerAffiliations:[OWNER]){
      totalCount
      nodes{ stargazerCount
        languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name } } } }
    }
    repositoriesContributedTo(first:100, includeUserRepositories:false,
        contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY]){
      totalCount
      nodes{ stargazerCount
        languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name } } } }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "profile-metrics"})
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit("GraphQL errors: " + json.dumps(payload["errors"])[:500])
    return payload["data"]["user"]


def collect(user):
    c = user["contributionsCollection"]
    owned = user["repositories"]["nodes"]
    contrib = user["repositoriesContributedTo"]["nodes"]

    langs = {}
    for repo in owned + contrib:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total_bytes = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

    return {
        "contributions": c["contributionCalendar"]["totalContributions"],
        "commits": c["totalCommitContributions"],
        "prs": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "reviews": c["totalPullRequestReviewContributions"],
        "stars": sum(r["stargazerCount"] for r in owned),
        "repos": user["repositories"]["totalCount"] + user["repositoriesContributedTo"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "langs": [(n, round(100 * s / total_bytes, 1)) for n, s in top],
    }


def tile(x, y, w, h, value, label, delay):
    return f'''<g opacity="1">
  <animate attributeName="opacity" begin="0s" dur="{delay + 0.5:.2f}s" values="0;0;1"
    keyTimes="0;{delay / (delay + 0.5):.4f};1" fill="freeze"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{PANEL}" stroke="{LINE_2}" stroke-width="1.3"/>
  <rect x="{x}" y="{y}" width="3.5" height="{h}" rx="1.7" fill="{G_MAIN}" opacity="0.85"/>
  <text x="{x + 20}" y="{y + 40}" font-family="{MONO}" font-size="29" font-weight="700" fill="{G_BRIGHT}">{value}</text>
  <text x="{x + 20}" y="{y + 60}" font-family="{MONO}" font-size="10" fill="{DIM}" letter-spacing="1.6">{label}</text>
</g>'''


def build(d):
    W, H = 1000, 300
    tiles = [
        (f'{d["contributions"]:,}', "CONTRIBUTIONS / 12 MO"),
        (f'{d["commits"]:,}', "COMMITS"),
        (f'{d["prs"]:,}', "PULL REQUESTS"),
        (f'{d["repos"]:,}', "REPOSITORIES"),
    ]
    tw, th, gap = 220, 78, 14
    ts = "\n".join(
        tile(48 + (i % 2) * (tw + gap), 92 + (i // 2) * (th + gap), tw, th, v, l, 0.2 + i * 0.1)
        for i, (v, l) in enumerate(tiles))

    bx, bw = 560, 392
    shades = [G_BRIGHT, G_MAIN, "#17B44A", G_DEEP, "#0B6E2E", "#0A4F22"]
    bars = []
    for i, (name, pct) in enumerate(d["langs"]):
        y = 96 + i * 30
        fill = max(6.0, bw * pct / 100)
        delay = 0.5 + i * 0.1
        bars.append(f'''<g opacity="1">
  <animate attributeName="opacity" begin="0s" dur="{delay + 0.5:.2f}s" values="0;0;1"
    keyTimes="0;{delay / (delay + 0.5):.4f};1" fill="freeze"/>
  <text x="{bx}" y="{y}" font-family="{MONO}" font-size="12" fill="{TXT}">{name}</text>
  <text x="{bx + bw}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{DIM}">{pct}%</text>
  <rect x="{bx}" y="{y + 6}" width="{bw}" height="6" rx="3" fill="#0C1710"/>
  <rect x="{bx}" y="{y + 6}" width="{fill:.1f}" height="6" rx="3" fill="{shades[i % len(shades)]}">
    <animate attributeName="width" begin="0s" dur="{delay + 0.9:.2f}s" values="0;0;{fill:.1f}"
      keyTimes="0;{delay / (delay + 0.9):.4f};1" calcMode="spline"
      keySplines="0 0 1 1;0.16 1 0.3 1" fill="freeze"/>
  </rect>
</g>''')

    stamp = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub metrics">
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M 24 0 L 0 0 0 24" fill="none" stroke="{LINE}" stroke-width="1" opacity="0.85"/>
  </pattern>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{G_DEEP}" stop-opacity="0"/>
    <stop offset="45%" stop-color="{G_MAIN}"/>
    <stop offset="100%" stop-color="{G_DEEP}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{G_MAIN}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{G_MAIN}" stop-opacity="0.14"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#grid)" opacity="0.4"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="14" fill="none" stroke="{LINE}" stroke-width="1.5"/>
<text x="48" y="48" font-family="{MONO}" font-size="12" fill="{G_DEEP}" letter-spacing="3">// LAST 12 MONTHS</text>
<text x="48" y="76" font-family="{MONO}" font-size="19" font-weight="700" fill="{TXT}" letter-spacing="1">the receipts</text>
<text x="{W - 48}" y="48" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DIM_2}" letter-spacing="1.6">SELF GENERATED &#183; {stamp}</text>
<text x="{bx}" y="76" font-family="{MONO}" font-size="12" fill="{G_DEEP}" letter-spacing="3">// LANGUAGES BY VOLUME</text>
{ts}
{"".join(bars)}
<g opacity="0.55">
  <rect x="0" y="-70" width="{W}" height="70" fill="url(#scan)">
    <animate attributeName="y" values="-70;{H}" dur="8s" repeatCount="indefinite"/>
  </rect>
</g>
<rect x="0" y="{H - 3}" width="{W}" height="3" fill="url(#edge)" opacity="0.75"/>
</svg>'''


def main():
    login = os.environ.get("LOGIN") or "majedahdab2005"
    token = os.environ.get("GITHUB_TOKEN")
    out = os.environ.get("OUT", "assets/metrics.svg")
    if os.environ.get("MOCK"):
        data = {"contributions": 1284, "commits": 1043, "prs": 62, "issues": 18,
                "reviews": 27, "stars": 14, "repos": 23, "followers": 3,
                "langs": [("TypeScript", 71.4), ("CSS", 9.2), ("JavaScript", 7.8),
                          ("PLpgSQL", 5.1), ("Python", 3.9), ("Shell", 2.6)]}
    else:
        if not token:
            sys.exit("GITHUB_TOKEN missing")
        data = collect(fetch(login, token))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write(build(data))
    print("wrote", out, json.dumps({k: v for k, v in data.items() if k != "langs"}))


if __name__ == "__main__":
    main()
