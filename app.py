from flask import Flask, render_template, request
from app.wiki_summary import summarize_wikipedia, originalLink, force_summary
from app.url_summary import summarize_ai

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/url")
def url():
    return render_template("url.html")

@app.route("/wiki")
def wiki():
    return render_template("wiki.html")

@app.route("/summaryurl", methods=['POST'])
def sumurl():
    url = request.form['url']
    summary,fullurl,safe=summarize_ai(url)
    print(f"[디버깅] 입력 URL: {url}, 변환된 전체 URL: {fullurl}, safe 여부: {safe}")

    return render_template("urlresult.html", summary=summary, url=fullurl, safe=safe)

@app.route("/force_summaryurl", methods=["POST"])
def forceurl():
    url = request.form['url']
    summary,fullurl, _= summarize_ai(url)
    return render_template("urlresult.html", summary=summary, url=fullurl, safe=True)

@app.route("/summarywiki", methods=['POST'])
def sumwiki():
    keyword = request.form['keyword']
    result = summarize_wikipedia(keyword)
    
    if isinstance(result, dict) and result.get("disambiguation"):
        return render_template("wikiresult.html", options=result["options"], message=result["message"], summary=None, original=None)

    summary=result
    if summary.startswith("검색어가 모호합니다.") or summary.startswith("검색 결과가") or summary.startswith("알 수"):
        original = None
    else:
        original = originalLink(keyword)

    return render_template("wikiresult.html", summary=summary, original=original)

@app.route("/force_summary", methods=["POST"])
def forced():
    keyword = request.form['keyword']
    summary, original = force_summary(keyword)
    return render_template("wikiresult.html", summary=summary, original=original, options=None, message=None)




if __name__ == "__main__": 

    app.run(host="0.0.0.0", port=8000, debug=True)