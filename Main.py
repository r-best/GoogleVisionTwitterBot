from datetime import datetime
import re
import json
import tweepy
from google.cloud import vision

# Constants
BOT_NAME = 'bobbys_bot_test'

# Read in the last update time from file
date_file = open('lastupdate.txt', 'r+')
temp = re.split(' |-|:|\\.', date_file.readline())
temp = [int(x) for x in temp]
last_update = datetime(temp[0], temp[1], temp[2], temp[3]+4, temp[4], temp[5])
print("LAST UPDATE: "+str(last_update))

# Read in the JSON file that contains the API keys for Twitter and the project name for Google Vision
keys = json.loads(open('keys.json').read())

# Initialize Twitter API with keys from JSON file
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)

# Initialize a client for Google Vision API
vision_client = vision.Client(keys['vision_project_name'])

# Save new "last updated" time to save to file at end
new_update_time = datetime.now()

# Search for tweets containing the bot's screen name with an @ in front of it
tweets = api.search(q=('@'+BOT_NAME), rpp=100, show_user=1, include_entities=1)
for tweet in tweets:
    # Skip the tweet if it's already been replied to or it's a tweet made by the bot
    if tweet.created_at < last_update or tweet.user.screen_name == BOT_NAME:
        print("SKIP "+str(tweet.created_at))
        continue
    else:
        print("USE "+str(tweet.created_at))
    # Ensure the @ + screen name was an actual mention directed at the bot
    for mention in tweet.entities['user_mentions']:
        if mention['screen_name'] == BOT_NAME:
            if 'media' in tweet.entities:
                # Use Vision API to get image from tweet's media_url and detect labels in it
                image = vision_client.image(source_uri=tweet.entities['media'][0]['media_url'])
                labels = image.detect_labels()
                # Put together the text for the bot to tweet
                text = "@" + tweet.user.screen_name + " Your picture contains:\n"
                for i in range(0, labels.__len__()):
                    temp = text
                    temp += labels[i].description + " - {}%".format(round(labels[i].score * 100, 1))
                    if temp.__len__() > 140:  # Ensure text won't be over 140 chars
                        break
                    else:
                        text = temp

                    if i != labels.__len__()-1:
                        text += "\n"
                print(labels[0].description + " - {}%".format(round(labels[i].score * 100, 1)) + "  " + str(tweet.id))
                # Make tweet
                api.update_status(text, in_reply_to_status_id=tweet.id)
                break
            else:  # Tweet did not contain any images
                print("No image - " + str(tweet.id))
                api.update_status('@' + tweet.user.screen_name + ' ' + "Your tweet did not contain an image", in_reply_to_status_id=tweet.id)
                break

# Update file with new "last updated" time
date_file.seek(0)
date_file.write(str(new_update_time))
date_file.truncate()
date_file.close()