from flask import Flask, render_template, request
# from app.wiki_summary import summarize_wikipedia
# from app.url_summary import summarize_url

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
# @app.route("/summaryurl", methods=["POST"])
# def sumurl():
#     url = request.form['url']
#     summary = #modulename(url)
#     return render_template("result.html", summary=summary)

# @app.route("/summarywiki", methods=['POST'])
# def sumwiki():
#     keyword = request.form['keyword']
#     summary = #modulename(keyword)
#     return render_template("result.html", summary=summary)


if __name__ == "__main__": #이 파일이 직접 실행될때만 밑에 실행문이 실행된다

    app.run(host="0.0.0.0", port=8000, debug=True)