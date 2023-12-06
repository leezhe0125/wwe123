import firebase_admin
import requests

from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

@app.route("/")
def index():
    X = "作者:李哲 2023-12-6<br>"
    X += "<a href=/db>課程網頁</a><br>"
    X += "<a href=/wwe?nick=wwe>個人介紹及系統時間</a><br>"
    X += "<a href=/account>表單傳值</a><br>"
    X += "<br><a href=/read>讀取Firestore資料</a><br>"
    X += "<br><a href=/read2>人選之人─造浪者</a><br>"
    X += "<br><a href=/read3>圖書精選</a><br>"
    X += "<br><a href=/search>車禍查詢路口</a><br>"
    X += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    return X

@app.route("/db")
def db():
    return "<a href='https://drive.google.com/drive/folders/1JGHLQWpzT2QxSVPUwLxrIdYowijWy4h1'>海青班資料庫管理課程</a>"

@app.route("/wwe", methods=["GET", "POST"])
def wwe():
    tz = timezone(timedelta(hours=+8))
    now = str(datetime.now(tz))
    #now = str(datetime.now())
    user = request.values.get("nick")
    return render_template("alex.html", datetime=now, name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    import requests,json
url = "https://datacenter.taichung.gov.tw/swagger/OpenData/db36e286-1d2b-4784-99b9-3b0790dd9652"
Data = requests.get(url)
#print(Data.text)

JsonData = json.loads(Data.text)

Road = input("請輸入慾查詢的路段關鍵字:")

for x in JsonData:
	if Road in x["路口名稱"]:
		print(x["路口名稱"] + "總共發生了" + x["總件數"] + "次車禍")
		print("事故發生的主要原因是因爲" + x["主要肇因"])
		print()
        return Result
    else:
        return render_template("search.html")
        
@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("黃植達")    
    docs = collection_ref.get()
    for doc in docs:         
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"    
    return Result

@app.route("/read2")
def read2():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("人選之人─造浪者")    
    docs = collection_ref.order_by("birth").get()
    for doc in docs:         
        x = doc.to_dict()
        Result += "Name : " + x["name"] + ", Role : " + x["role"] + ", Birth : " + str(x["birth"]) + "<br>"    
    return Result

@app.route("/read3")
def read3():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")    
    docs = collection_ref.order_by("anniversary").get()
    for doc in docs:
        book = doc.to_dict()
        Result += "Title : <a href = " + book["url"] + ">" + book["title"] + "</a><br>"
        Result += "Author : " + book["author"] + "<br>"
        Result += "Anniversary : " + str(book["anniversary"]) + "<br>"
        Result += "<img src = " + book["cover"] + ">" + "</img><br>"
    return Result

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]
    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]
        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
            }
        db = firestore.client()
        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate


if __name__ == "__main__":
    app.run(debug=True)
