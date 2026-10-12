import feedparser
from google import genai
import os

# 1. 최신 Google GenAI 클라이언트 생성 (GEMINI_API_KEY 환경변수 자동 인식)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. 뉴스 RSS 가져오기
rss_urls = [
    "https://www.yna.co.kr/rss/news.xml", # 연합뉴스
    "https://moxie.foxnews.com/google-publisher/latest.xml", # Fox News
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml" # NYT
]

news_titles = []
for url in rss_urls:
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:
        news_titles.append(entry.title)

# 3. Gemini에게 뉴스 요약 요청
prompt = f"""
다음은 오늘 주요 뉴스 헤드라인입니다:
{news_titles}

정치, 경제, 사회 분야별 핵심 이슈를 각각 5개 이상 선정해서 한국어로 3줄 요약해줘.
"""

# 최신 Gemini 모델 호출
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

# 4. 요약 결과를 news_summary.txt 파일에 저장
with open("news_summary.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("뉴스 요약 완료!")
