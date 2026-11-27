
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime, timezone

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
SubElement(channel, "description").text = "苹果新闻网国际即时新闻 RSS"
SubElement(channel, "language").text = "zh-TW"
SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

seen = set()
count = 0

for a in soup.select("a[href]"):
    href = urljoin(URL, a.get("href", ""))
    title = a.get_text(" ", strip=True)

    if not title or len(title) < 8:
        continue

    if "/realtime/international/" not in href:
        continue

    if href.rstrip("/") == URL.rstrip("/"):
        continue

    if href in seen:
        continue

    seen.add(href)

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = href
    SubElement(item, "description").text = title
    SubElement(item, "guid", isPermaLink="true").text = href
    SubElement(item, "pubDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    count += 1
    if count >= 40:
        break

tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
print(f"RSS generated: {count} articles")
