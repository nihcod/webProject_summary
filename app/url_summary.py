import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
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

        title_tag = soup.find("strong", class_="title_post")
        title = title_tag.get_text(strip=True) if title_tag else "웹 페이지"

        mainct = (
            soup.find("article") or
            soup.find("main") or
            soup.find("div", {"id": "content"}) or
            soup.body
        )
        if not mainct:
            return title, None

        text = mainct.get_text(separator='\n')
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 40]
        content = '\n'.join(lines)

        return title, content
    except:
        return "웹 페이지", None
    
def summarize_ai(user_input):
    parse = urlparse(normal_url(user_input))
    domain = parse.netloc or parse.path
    safe = safeURL(domain)
    https = https_ok(domain)
    scheme="https" if https else "http"
    url = f"{scheme}://{domain}"

    title, fetch = fetch_text(url)
    if not fetch:
        return "페이지를 가져올 수 없습니다.", url, safe
    
    try:
        command=f'''다음은 어떤 웹페이지의 전체 텍스트야. \n
        주제는 "{title}"이야. 주제가 있다면 주제 위주로 설명해야돼.\n페이지의 전체 목적이나 소개가 아닌
        페이지 본문이 설명하고자 하는 핵심 주제와 내용을 10줄이내로 간결하게 요약해줘.\n
        이 텍스트는 메뉴나 블로그 소개, 사이트 설명 등을 포함할 수도 있는데 넌 그걸 다 제외하고
        본문 내용중 개념적인 부분, 기술적으로 중요한 내용을 요약해서 설명 해줘야해.\n
        특히 기술 문서나 블로그면 해당 페이지에서 설명하는 개념이나 기술, 동작방식 위주로 요약해 :
        \n{fetch[0:5000]}'''
        res = model.generate_content(command)
        return res.text.strip(), url, safe and https
    except Exception as e:
        return f"오류가 발생하였습니다! : {str(e)}", url, safe