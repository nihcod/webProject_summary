import requests
from bs4 import BeautifulSoup
import google.generativeai as ai

ai.configure(api_key="")

model = ai.GenerativeModel("gemini-2.0-flash")
blacklist_keywords = ["document.cookie", "window.location", "<script>", "onerror"]
#low level의 쿠키탈취, XSS등 방지 블랙리스트 키워드

def normal_url(user_input):
    if not user_input.startswith("http"):
        user_input="https://"+user_input

    return user_input
def https_ok(domain):
    test_url = [
        f"https://{domain}",
        f"https://www.{domain}" if not domain.startswith("www.") else f"https://{domain[4:]}"
    ]

    for url in test_url:
        try:
            response = requests.get(url, timeout=4)
            
            if response.url.startswith("https://"):
                return True
        except requests.exceptions.SSLError:
            return False
        except requests.exceptions.RequestException:
            continue  
    return False
    
def safeURL(url):
    url=url.lower()
    return not any(hack in url for hack in blacklist_keywords)

def fetch_text(url):
    try:
        res = requests.get(url, timeout=4)
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup.find_all(["script", "style", "aside", "footer", "nav", "header", "form", "iframe"]):
            tag.decompose()
        for code_tag in soup.find_all(["pre", "code", "textarea"]):
            code_tag.decompose()
        texts = []
        for el in soup.find_all(["p", "h1", "h2", "h3", "h4"]):
            text = el.get_text(strip=True)
            if text:
                texts.append(text)
        clean_lines = []
        for line in texts:
            if len(line) < 40:
                continue
            low = line.lower()
            if any(x in low for x in ["광고", "소개", "kakao", "google"]):
                continue
            clean_lines.append(line)
        content = "\n".join(clean_lines)
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "웹 페이지"
        return title, content if clean_lines else None
    except:
        return "웹 페이지", None

    
def summarize_ai(user_input):
    url = user_input if user_input.startswith("http") else "https://" + user_input
    title, fetch = fetch_text(url)
    if not fetch:
        return "페이지를 가져올 수 없습니다.", url, False
    command = f"""
            아래 웹페이지 본문을 읽고 핵심 개념과 주요 내용을 10줄 이내로 요약해줘.
            서론, 광고, 메뉴, 댓글 등 불필요한 내용은 모두 빼고 중요한 설명만 포함해줘.

            웹페이지 제목: {title}
            본문:  {fetch}
            """
    res = model.generate_content(command)
    return res.text.strip(), url, True
