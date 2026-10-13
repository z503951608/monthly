import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

URL = "https://github.com/trending?since=monthly"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_trending():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    repos = []
    # Trending仓库条目选择器，github页面更新时这里可能失效
    articles = soup.select("article.Box-row")
    for item in articles:
        try:
            title_tag = item.select_one("h2 a")
            full_name = title_tag.get("href").strip("/")
            repo_url = f"https://github.com/{full_name}"
            desc_tag = item.select_one("p")
            desc = desc_tag.get_text(strip=True) if desc_tag else ""
            lang_tag = item.select_one("span[itemprop='programmingLanguage']")
            lang = lang_tag.get_text(strip=True) if lang_tag else ""
            star_tag = item.select_one("a[href$='/stargazers']")
            stars = star_tag.get_text(strip=True) if star_tag else ""
            fork_tag = item.select_one("a[href$='/forks']")
            forks = fork_tag.get_text(strip=True) if fork_tag else ""

            repos.append({
                "full_name": full_name,
                "url": repo_url,
                "description": desc,
                "language": lang,
                "stars": stars,
                "forks": forks
            })
        except Exception as e:
            print(f"parse item error: {e}")
    return repos

def save_data(repos):
    now = datetime.now()
    date_str = now.strftime("%Y-%m")
    os.makedirs("data", exist_ok=True)
    json_path = f"data/trending-monthly-{date_str}.json"
    md_path = f"data/trending-monthly-{date_str}.md"

    # 保存JSON原始数据
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)

    # 生成Markdown清单
    md_lines = [f"# GitHub Trending Monthly {date_str}\n"]
    for idx, repo in enumerate(repos, 1):
        md_lines.append(f"{idx}. [{repo['full_name']}]({repo['url']})")
        md_lines.append(f"> {repo['description']}")
        md_lines.append(f"- Language: {repo['language']} | ⭐{repo['stars']} | 🍴{repo['forks']}\n")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Saved {len(repos)} repos to {json_path}, {md_path}")

if __name__ == "__main__":
    repo_list = fetch_trending()
    save_data(repo_list)
