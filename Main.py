import tweepy

auth = tweepy.OAuthHandler('iuyLxnTlK5rROK2hHungsU02p', '1CTqGkLtfUEy8i7jcfZZ7QbZb0XuUTx3Kb8gOhiiOYcGPAYde6')
auth.set_access_token('857733332469243905-quu35YvdZoqKZZiXpgdG6W1TOX6FaAy', 'KMAUnfTRIPPomtPViJSwoSK6MIyVX3SNCPBQDrdWGQbwK')

api = tweepy.API(auth)

public_tweets = api.home_timeline()
# for tweet in public_tweets:
#    print(tweet.text)
print(public_tweets[1].coordinates)

#api.update_with_media('image.png', 'Testing status with media')

#print(api.reverse_geocode(17.750163, 142.500000))