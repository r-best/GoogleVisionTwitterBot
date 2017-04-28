import tweepy
import json
from google.cloud import vision

done_tweets_file = open('doneTweets.txt', 'r+')
done_tweets = done_tweets_file.readlines()
done_tweets = [x.strip() for x in done_tweets]

keys = json.loads(open('keys.json').read())

vision_client = vision.Client('crafty-plateau-166018')

auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

api = tweepy.API(auth)

tweets = api.search(q='@bobbys_bot_test', rpp=100, show_user=1, include_entities=1)
for tweet in tweets:
    if done_tweets.__contains__(str(tweet.id)) or tweet.user.screen_name == 'bobbys_bot_test':
        continue
    for mention in tweet.entities['user_mentions']:
        if mention['screen_name'] == 'bobbys_bot_test':
            if 'media' in tweet.entities:
                image = vision_client.image(source_uri=tweet.entities['media'][0]['media_url'])
                labels = image.detect_labels()
                text = "Your picture contains:\n"
                for i in range(0, labels.__len__()):
                    temp = text
                    temp += labels[i].description + " - {}%".format(round(labels[i].score * 100, 1))
                    if temp.__len__() > 140:
                        break
                    else:
                        text = temp

                    if i != labels.__len__()-1:
                        text += "\n"
                print(text)
                print(str(tweet.id))
                api.update_status('@' + tweet.user.screen_name + ' ' + text, in_reply_to_status_id=tweet.id)
                done_tweets.append(tweet.id)
                done_tweets_file.writelines(str(tweet.id) + '\n')
            else:
                print(str(tweet.id))
                api.update_status('@' + tweet.user.screen_name + ' ' + "Your tweet did not contain an image", in_reply_to_status_id=tweet.id)
                done_tweets.append(tweet.id)
                done_tweets_file.writelines(str(tweet.id) + '\n')
