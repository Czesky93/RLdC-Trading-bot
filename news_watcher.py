import requests
import json
import tweepy

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API do Twittera i RSS.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

TWITTER_API_KEY = config["TWITTER_API_KEY"]
TWITTER_API_SECRET = config["TWITTER_API_SECRET"]
TWITTER_ACCESS_TOKEN = config["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = config["TWITTER_ACCESS_SECRET"]
NEWS_API_URL = "https://newsapi.org/v2/everything?q=crypto&apiKey=" + config["NEWS_API_KEY"]

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

def get_crypto_news():
    """Pobiera najnowsze newsy o krypto"""
    response = requests.get(NEWS_API_URL)
    articles = response.json().get("articles", [])
    return [article["title"] for article in articles[:5]]

def get_twitter_trends():
    """Pobiera najnowsze tweety o krypto"""
    tweets = twitter_api.search_tweets(q="crypto OR bitcoin OR ethereum", lang="en", count=5)
    return [tweet.text for tweet in tweets]

def analyze_sentiment(news_list):
    """Prosta analiza sentymentu (pozytywne/negatywne)"""
    positive_keywords = ["bullish", "breakout", "gains", "up", "surge"]
    negative_keywords = ["crash", "sell-off", "dump", "collapse", "fear"]

    sentiment_score = 0
    for news in news_list:
        if any(word in news.lower() for word in positive_keywords):
            sentiment_score += 1
        elif any(word in news.lower() for word in negative_keywords):
            sentiment_score -= 1

    return "Pozytywny" if sentiment_score > 0 else "Negatywny" if sentiment_score < 0 else "Neutralny"

if __name__ == "__main__":
    news = get_crypto_news()
    tweets = get_twitter_trends()

    print("📰 Ostatnie newsy:")
    for n in news:
        print(f"- {n}")

    print("
🐦 Ostatnie tweety:")
    for t in tweets:
        print(f"- {t}")

    sentiment = analyze_sentiment(news + tweets)
    print(f"
📊 Sentiment rynku: {sentiment}")
