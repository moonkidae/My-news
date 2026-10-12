import feedparser
from google import genai
import os

# 1. API 키 확인
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

# 2. 뉴스 RSS 가져오기 (헤드라인 파싱 안정화)
rss_urls = [
    "https://www.yna.co.kr/rss/news.xml", # 연합뉴스
    "https://moxie.foxnews.com/google-publisher/latest.xml", # Fox News
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml" # NYT
]

news_titles = []
for url in rss_urls:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = getattr(entry, 'title', '')
            if title:
                news_titles.append(title)
    except Exception as e:
        print(f"RSS 수집 중 오류 ({url}): {e}")

print(f"수집된 뉴스 개수: {len(news_titles)}")

# 3. Gemini API 호출
client = genai.Client(api_key=api_key)

prompt = f"""
다음은 오늘 주요 뉴스 헤드라인입니다:
{news_titles}

정치, 경제, 사회 분야별 핵심 이슈를 각각 5개 이상 선정해서 한국어로 3줄 요약해줘.
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

# 4. 요약 결과를 news_summary.txt 파일에 저장
with open("news_summary.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("뉴스 요약이 성공적으로 완료되었습니다!")
