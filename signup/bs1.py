from bs4 import BeautifulSoup as bs
import requests
from pytube import YouTube
from flask import Flask, render_template,redirect,request,url_for,flash

app = Flask(__name__)
app.debug = True

@app.route("/")
def videos():
	base = "https://www.youtube.com/results?search_query="
	qstring = "engineering+technology"

	r = requests.get(base+qstring)
	print(r)
	page = r.text
	soup=bs(page,'html.parser')

	vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})
	print(vids)
	videolist=[]
	c = 0
	for v in vids:
		if(c<=6):
			tmp = 'https://www.youtube.com' + v['href']
			tmp = tmp.replace("watch?v=", "embed/")
			videolist.append(tmp)
			c = c+1
	return render_template("tempvid.html",video1 = videolist)
	
if __name__ == '__main__':
    app.run()
