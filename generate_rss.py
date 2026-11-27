
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime, timezone
import re

URL = "https://news.nextapple.com/realtime/international/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "Next Apple 国际新闻"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "苹果新闻网国际新闻，包含标题、新闻链接及内容简介"
SubElement(channel, "language").text = "zh-TW"
SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

seen = set()
count = 0

for a in soup.select("a[href]"):
    href = urljoin(URL, a.get("href", ""))
    path = urlparse(href).path

    # 正确的国际新闻文章路径：/international/日期/文章ID
    if not re.match(r"^/international/\d{8}/[A-Za-z0-9]+", path):
        continue

    title = a.get_text(" ", strip=True)
    if not title or len(title) < 8 or href in seen:
        continue

    seen.add(href)

    # 尝试从新闻卡片附近获取内容简介
    description = title
    for parent in a.parents:
        text = parent.get_text(" ", strip=True)
        if title in text and 80 <= len(text) <= 1200:
            description = text.replace(title, "", 1).strip()
            if description:
                break

    # 从链接日期提取发布时间
    date_match = re.search(r"/international/(\d{8})/", path)
    pubdate = datetime.now(timezone.utc)
    if date_match:
        try:
            pubdate = datetime.strptime(date_match.group(1), "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = href
    SubElement(item, "description").text = description
    SubElement(item, "guid", isPermaLink="true").text = href
    SubElement(item, "pubDate").text = pubdate.strftime("%a, %d %b %Y %H:%M:%S GMT")

    count += 1
    if count >= 40:
        break

ElementTree(rss).write("feed.xml", encoding="utf-8", xml_declaration=True)
print(f"RSS generated: {count} articles")
