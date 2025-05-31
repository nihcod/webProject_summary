import wikipedia
from urllib.parse import quote
def summarize_wikipedia(keyword, lang='ko', max_sentences=8):
    wikipedia.set_lang(lang)

    try:
        summary = wikipedia.summary(keyword, sentences=max_sentences)
        return summary

    except wikipedia.exceptions.DisambiguationError as e:
        return {
            "disambiguation": True,
            "options": e.options[:5],
            "message": f"검색어가 모호합니다. 다음 중에서 선택해 주세요:"
        }
    except wikipedia.exceptions.PageError:
        return "검색 결과가 없습니다."

    except Exception as e:
        return f"알 수 없는 오류가 발생 하였습니다.: {str(e)}"
    
def force_summary(keyword, lang='ko', max_sentences=8):
    wikipedia.set_lang(lang)
    
    try:
        results = wikipedia.search(keyword)
        if not results:
            return "문서를 찾을 수 없습니다.", None

        for title in results:
            try:
                summary = wikipedia.summary(title, sentences=max_sentences)
                link = f"https://{lang}.wikipedia.org/wiki/{quote(title)}"
                return summary, link
            except wikipedia.exceptions.DisambiguationError:
                continue
            except wikipedia.exceptions.PageError:
                continue
        return "항목을 찾을 수 없습니다.", None

    except Exception as e:
        return f"알 수 없는 오류 발생: {str(e)}", None
    
def originalLink(keyword, lang='ko'):
    wikipedia.set_lang(lang)
    page=wikipedia.page(keyword)
    encoded=quote(keyword)
    return f"https://{lang}.wikipedia.org/wiki/{encoded}"
