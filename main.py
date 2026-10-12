import urllib.request
import xml.etree.ElementTree as ET
import json
import os

def get_rss_titles(url):
    titles = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            # RSS2.0 / Atom 피드 대응
            for item in root.findall('.//item')[:10]:
                title = item.find('title')
                if title is not None and title.text:
                    titles.append(title.text)
    except Exception as e:
        print(f"RSS 수집 오류 ({url}): {e}")
    return titles

# 1. 뉴스 RSS 수집
rss_urls = [
    "https://www.yna.co.kr/rss/news.xml", # 연합뉴스
    "https://moxie.foxnews.com/google-publisher/latest.xml", # Fox News
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml" # NYT
]

all_titles = []
for url in rss_urls:
    all_titles.extend(get_rss_titles(url))

# 2. Gemini REST API 직접 호출
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

prompt = f"""
다음은 오늘 주요 뉴스 헤드라인입니다:
{all_titles}

정치, 경제, 사회 분야별 핵심 이슈를 각각 5개 이상 선정해서 한국어로 3줄 요약해줘.
"""

api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}
data = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

req = urllib.request.Request(api_url, data=json.dumps(data).encode('utf-8'), headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        summary_text = result['candidates'][0]['content']['parts'][0]['text']

    # 3. 요약 결과를 news_summary.txt 파일에 저장
    with open("news_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary_text)

    print("뉴스 요약이 성공적으로 완료되었습니다!")

except Exception as e:
    print(f"Gemini API 호출 중 오류 발생: {e}")
    raise e
