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