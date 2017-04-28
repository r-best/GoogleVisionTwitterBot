import tweepy
import json
from google.cloud import vision

# Read in the file of tweet IDs that have already been replied to
# Used to avoid replying to the same tweet twice
done_tweets_file = open('doneTweets.txt', 'r+')
done_tweets = done_tweets_file.readlines()
done_tweets = [x.strip() for x in done_tweets]

# Initialize a client for Google Vision API
vision_client = vision.Client('crafty-plateau-166018')

# Read in the JSON file that contains the API keys for Twitter
keys = json.loads(open('keys.json').read())

# Initialize Twitter API with keys from JSON file
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)

# Search for tweets containing the bot's screen name with an @ in front of it
tweets = api.search(q='@bobbys_bot_test', rpp=100, show_user=1, include_entities=1)
for tweet in tweets:
    # Skip the tweet if it's already been replied to or it's a tweet made by the bot
    if done_tweets.__contains__(str(tweet.id)) or tweet.user.screen_name == 'bobbys_bot_test':
        continue
    # Ensure the @ + screen name was an actual mention directed at the bot
    for mention in tweet.entities['user_mentions']:
        if mention['screen_name'] == 'bobbys_bot_test':
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
                # Make tweet and add the mentioning tweet's ID to the list of tweets that have been replied to
                api.update_status(text, in_reply_to_status_id=tweet.id)
                done_tweets.append(tweet.id)
                done_tweets_file.writelines(str(tweet.id) + '\n')
                break
            else:  # Tweet did not contain any images
                print("No image - " + str(tweet.id))
                api.update_status('@' + tweet.user.screen_name + ' ' + "Your tweet did not contain an image", in_reply_to_status_id=tweet.id)
                done_tweets.append(tweet.id)
                done_tweets_file.writelines(str(tweet.id) + '\n')
                break
