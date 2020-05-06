from flask import Flask, request, redirect
import requests, json
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from search.search_blueprint import search_app
import config
import os
import random

account_sid = config.TWILIO_ID
auth_token = config.TWILIO_SECRET
client = Client(account_sid, auth_token)

app = Flask(__name__)

app.register_blueprint(search_app, url_prefix='/search')

'''
Handle and respond to User text.

Takes SMS or MMS and returns appropriate response.
'''
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
	# get body of text message
	body = request.values.get('Body', None)
	media = request.values.get('MediaUrl0', None)
    # Respond to incoming text messages.
    # Start our TwiML response
	resp = MessagingResponse()

    # Determine the right reply for this message
	if body == 'Ernie' or body == 'ernie':
		msg = resp.message("Here's a random image of Ernie!")
		random_ernie_media = random_ernie();
		msg.media(random_ernie_media)
	elif body == "":
		r = perform_search(media)
		best_guess = r.json()['best_guess']
		msg = resp.message(best_guess)
	else:
		msg = resp.message("Type Ernie or send a picture for us to classify!")

	return str(resp);

'''
Search for dog type.

Use MRISA search blueprint by vivithemage to perform reverse image lookup on Google
'''
def perform_search(image_url):
	data = {
    	"image_url":image_url,
    	"resized_images":False, # Or True
    	"cloud_api":True
	}

	url = "http://localhost:5000/search"

	headers = {'Content-type': 'application/json'}
	
	r = requests.post(url, headers=headers, data=json.dumps(data))

	return r;

'''
Get picture of Ernie.

Retrieves random image of Ernie from storage and returns to append to response to User.
'''
def random_ernie():
	# pick random image from storage and return
	static_folder = config.static_path;
	random_image = random.choice(os.listdir(static_folder));

	# Do something with the loaded image_file
	# with open(os.path.join(static_folder, random_image), 'rb') as image_file:
	media_path = config.root + random_image;
	
	return media_path;

'''
Define main arguments.

Use MRISA configuration details.
'''
def main():
    parser = argparse.ArgumentParser(description='Meta Reverse Image Search API')
    parser.add_argument('-p', '--port', type=int, default=5000, help='port number')
    parser.add_argument('-d','--debug', action='store_true', help='enable debug mode')
    parser.add_argument('-c','--cors', action='store_true', default=False, help="enable cross-origin requests")
    parser.add_argument('-a', '--host', type=str, default='0.0.0.0', help="sets the address to serve on")
    args = parser.parse_args()

    if args.debug:
        app.debug = True

    if args.cors:
        CORS(app, resources=r'/search/*')
        app.config['CORS_HEADERS'] = 'Content-Type'

        global search
        search = cross_origin(search)
        print(" * Running with CORS enabled")


    app.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()