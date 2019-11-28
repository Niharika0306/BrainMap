from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
import threading
import argparse
import datetime
import imutils
import time
import cv2
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
	videolist=[]
	base = "https://www.youtube.com/results?search_query="
	qstring = topicName

	r = requests.get(base+qstring)
	print(r)
	page = r.text
	soup=bs(page,'html.parser')

	vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})
	print(vids)
	
	c = 0
	for v in vids:
		if(c<6):
			tmp = 'https://www.youtube.com' + v['href']
			tmp = tmp.replace("watch?v=", "embed/")
			videolist.append(tmp)
			c = c+1
	with open('imageprocessing.txt', 'r') as f:
		data = f.read()
	return render_template('page3.html',video1 = videolist,topicName = topicName, data=data)

outputFrame = None
lock = threading.Lock()

# initialize a flask object


# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/stream")
def stream():
	# return the rendered template
	return render_template("videostream.html")

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock

	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)

		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)

			# cehck to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()
		
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution



if __name__ == '__main__':
	t = threading.Thread(target=detect_motion, args=(32, ))
	t.daemon = True	
	t.start()
	app.run(threaded=True, use_reloader=False)
	
vs.stop()