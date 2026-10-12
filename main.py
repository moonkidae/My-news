import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import os

# 1. RSS 뉴스 헤드라인 수집 함수
def get_rss_titles(url):
    titles = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item')[:10]:
                title = item.find('title')
                if title is not None and title.text:
                    titles.append(title.text)
    except Exception as e:
        print(f"RSS 수집 중 제외: {e}")
    return titles

# RSS 주소
rss_urls = [
    "https://www.yna.co.kr/rss/news.xml", # 연합뉴스
    "https://moxie.foxnews.com/google-publisher/latest.xml", # Fox News
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml" # NYT
]

all_titles = []
for url in rss_urls:
    all_titles.extend(get_rss_titles(url))

print(f"수집된 헤드라인 수: {len(all_titles)}")

# 2. Gemini API 호출 (외부 라이브러리 없이 HTTP 요청)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY가 없습니다.")

prompt = f"""
다음은 오늘 주요 뉴스 헤드라인입니다:
{all_titles}

정치, 경제, 사회 분야별 핵심 이슈를 각각 5개 이상 선정해서 한국어로 3줄 요약해줘.
"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}
payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode('utf-8'))
    summary_text = result['candidates'][0]['content']['parts'][0]['text']

# 3. news_summary.txt 파일 생성
with open("news_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary_text)

print("성공적으로 뉴스 요약이 완료되었습니다!")
