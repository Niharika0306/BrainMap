from flask import Flask, render_template,redirect,request,url_for,flash
import sqlite3 as  db
import feedparser
from indicoio import config, text_tags
from bs4 import BeautifulSoup as bs
import requests

config.api_key = "cfa7082e0a98abd1aaf9f085f9a850b1"

app = Flask(__name__)
app.debug = True

feedt = "https://www.sciencedaily.com/rss/top/technology.xml"
feedh = "http://feeds.bbci.co.uk/news/health/rss.xml"
feede =  "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
feedsp = "https://www.sciencedaily.com/rss/space_time.xml"

# login_manager = LoginManager()
# login_manager.init_app(app)



def sql_query(query):
	connection = db.connect("brainmap.db")
	connection.row_factory =db.Row 
	cursor = connection.cursor()
	cursor.execute(query)
	rows = cursor.fetchall()
	connection.close()
	return rows

def sql_insert(name,username,password,emailid,h,s,t,e):
	connection = db.connect("brainmap.db")
	connection.row_factory =db.Row 
	cursor = connection.cursor()
	cursor.execute('''INSERT INTO User (Name,Emailid,Username,Password,Space,Technology,Environment,Healthcare,Credits) 
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
		''',(name,emailid,username,password,s,t,e,h,30))
	connection.commit()

	connection.close()
	return 1







def thresholded(tags, minimum):
	""" 
	Remove all tags with probability less than `minimum` 
	"""
	return dict((category, prob) for category, prob in tags.items()
	        	if prob > minimum)

def likely_tag(tags, minimum=0.1):
	""" 
	Threshold tags, then get the tag with the highest probability.
	If no tag probability exceeds the minimum, return the string 'none'
	"""
	trimmed = thresholded(tags, minimum) or {'none': 0}
	return max(trimmed, key=lambda key: trimmed[key])

def parsed(entry):
	"""
	Strip unnecessary content from the return of feedparser, 
	and augment with the output of indico's `text_tags` API
	"""
	return {
		'title': entry['title'],
		'link': entry['link'],
		'tag': likely_tag(entry['tags'])
	}

@app.route('/')
def main():
	entries = []
	entry = get_feeds(feede)
	entries.extend(entry)
	entry = get_feeds(feedsp)
	entries.extend(entry)
	entry = get_feeds(feedt)
	entries.extend(entry)
	entry = get_feeds(feedh)
	entries.extend(entry)
	return render_template('index.html', entries=entries)
	
	
@app.route('/about')
def about_us():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')







@app.route('/log',methods=['GET','POST'])
def log():
	if(request.method=="GET"):
		res = sql_query('''SELECT *FROM User''')
		msg = 'SELECT * FROM User'
	return render_template('log.html',data = res,msg = msg)

@app.route('/signup/',methods=['GET','POST'])
def signup():
	# if(request.method=="POST"):
	return render_template('signup.html')


def get_feeds(feed):
	entries = feedparser.parse(feed)['entries']
	titles = [entry.get('title') for entry in entries]
	#title_tags = text_tags(titles)
	for entry, tags in zip(entries, titles):
		entry['tags'] = tags
	entries = [entry for entry in entries]
	return entries


@app.route('/signed_in',methods=['GET','POST'])
def signed_in():
	if(request.method=="POST"):
		name = request.form['name']
		username = request.form['username']
		emailid = request.form['email']
		password = request.form['password']
		checklist = request.form.getlist('preference')
		h = 0
		s = 0
		t= 0
		e = 0
		if 'envi' in checklist:
			e = 1
		if 'space' in checklist:
			s = 1
		if 'tech' in checklist:
			t = 1
		if 'health' in checklist:
			h = 1
		sql_insert(name,username,password,emailid,h,s,t,e)
		print(checklist)
		entries = []
		if(e==1):
			print("feed env")
			entry = get_feeds(feede)
			entries.extend(entry)
		if(s==1):
			print("feed space")
			entry = get_feeds(feedsp)
			entries.extend(entry)
		if(t==1):
			print("feed tech")
			entry = get_feeds(feedt)
			entries.extend(entry)
		if(h==1):
			print("feed health")
			entry = get_feeds(feedh)
			entries.extend(entry)

	return render_template('index.html',entries=entries)

@app.route('/tech')
def tech():
	return render_template('tech.html')

@app.route('/envi')
def envi():
	return render_template('envi.html')


@app.route('/page3/<topicName>')
def page3(topicName):
	base = "https://www.youtube.com/results?search_query="
	qstring = topicName

	r = requests.get(base+qstring)
	print(r)
	page = r.text
	soup=bs(page,'html.parser')

	vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})
	print(vids)
	videolist=[]
	c = 0
	for v in vids:
		if(c<6):
			tmp = 'https://www.youtube.com' + v['href']
			tmp = tmp.replace("watch?v=", "embed/")
			videolist.append(tmp)
			c = c+1
	return render_template('page3.html',video1 = videolist,topicName = topicName)

if __name__ == '__main__':
    app.run()
