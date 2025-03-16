import tweepy
import time
import requests
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from datetime import datetime, timedelta
from tweepy import TweepyException

# Load the model and tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# open ai key

API_KEY_AI = 'YOUR_API_KEY_HERE'
# Twitter API credentials
API_KEY = 'YOUR_API_KEY_HERE'
API_KEY_WEATHER = 'YOUR_API_KEY_HERE'
API_SECRET_KEY = 'YOUR_SECRET_KEY'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_SECRET_ACCESS_TOKEN'
BEARER_TOKEN = 'YOUR_BEARER_TOKEN'
CLIENT_ID ='YOUR_CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'
# Authenticate to Twitter
client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_SECRET_KEY,
                       access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)


# Keywords to track
keywords = ["chennai rains", "chennai weather", "#Chennai_Rains"]

# Time interval in seconds
TIME_INTERVAL = 60 * 15  # 15 minutes

# Retweet limit per day
RETWEET_LIMIT = 45

# Initialize the retweet counter and reset time
retweet_count = 0
next_reset_time = datetime.now() + timedelta(days=1)

# Replace with your actual API key and location key
API_KEY = 'YOUR_API_KEY'
API_KEY_MINUTES = 'MINUTES_API_KEY'
LOCATION_KEY = 'LOCATION_KEY'  
LOCATION_COORDINATES= "COORDINATES"

# Construct the URL for the current conditions endpoint
url = f"https://dataservice.accuweather.com/currentconditions/v1/{LOCATION_KEY}?apikey={API_KEY}"
def get_min_update(api_key, location_key):
        # Construct the URL for the current conditions endpoint
    url = f"http://dataservice.accuweather.com/forecasts/v1/minute?q={location_key}&apikey={api_key}"

    # Make the request to the AccuWeather API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        current_weather = response.json()
        if current_weather:
            # Create a formatted string with essential weather details
            weather_summary = (
                f"Currently in Chennai, Tamilnadu, India \n\n"
                f"🌦️ Condition: {current_weather['Summary']['Phrase']}\n\n"              
                f"For more info, visit \n {current_weather['Link']}\n" 
            )
            return weather_summary
        else:
            return "No weather data found."
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_daily_update(api_key, location_key):
        # Construct the URL for the current conditions endpoint
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}?apikey={api_key}"

    # Make the request to the AccuWeather API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        current_weather = response.json()
        #headline = current_weather['Headline']
        #daily_forecast = generate_tweet(current_weather)
        return current_weather 
    
def get_w_update(api_key, location_key):
    url = f"https://api.weatherapi.com/v1/current.json?q={location_key}&key={api_key}"
    # Make the request to the AccuWeather API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        current_weather = response.json()
        #headline = current_weather['Headline']
        #daily_forecast = generate_tweet(current_weather)
        return current_weather 

    
# Function to generate a tweet
def generate_daily_w(data):
    region = data['location']['region']
    country = data['location']['country']
    
    condition = data['current']['condition']['text']
    temp_c = data['current']['temp_c']
    temp_f = data['current']['temp_f']
    feelslike_c = data['current']['feelslike_c']
    feelslike_f = data['current']['feelslike_f']
    wind_kph = data['current']['wind_kph']

    # Construct a tweet prompt with new lines
    tweet_prompt = (
        f"Weather Update for Chennai, {region}, {country}:\n\n"
        f"🌦️ Condition : {condition}\n"
        f"🌡️ Temperature is {temp_c}°C ({temp_f}°F)\n"
        f"☀️ Feels Like {feelslike_c}°C ({feelslike_f}°F)\n"
        f"🍃 Wind Speed is {wind_kph} kph\n"
        f"Stay safe! 🌞\n\n"
        f"Follow @ChennaiWthr for more updates."
    )
    
    return tweet_prompt    
    
def generate_w_tweet(weather_response):
    # Extract relevant information from the JSON response
    headline_text = weather_response['Headline']['Text']
    effective_date = weather_response['Headline']['EffectiveDate']
    temperature_min = weather_response['DailyForecasts'][0]['Temperature']['Minimum']['Value']
    temperature_max = weather_response['DailyForecasts'][0]['Temperature']['Maximum']['Value']
    day_icon_phrase = weather_response['DailyForecasts'][0]['Day']['IconPhrase']
    night_icon_phrase = weather_response['DailyForecasts'][0]['Night']['IconPhrase']

    # Create a prompt for the model
    prompt = (
        f"Create a tweet with less than 240 characters about the weather alert: "
        f"{headline_text}. Effective Date: {effective_date}. Temperature range: "
        f"{temperature_min}°F to {temperature_max}°F. Day: {day_icon_phrase}, Night: {night_icon_phrase}."
    )

    # Generate text using the model
    generated_text = model.generate(prompt, max_length=240, num_return_sequences=1)
    
    return generated_text[0]


def get_current_weather(api_key, location_key):
    # Construct the URL for the current conditions endpoint
    url = f"https://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={api_key}&details=true"

    # Make the request to the AccuWeather API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        current_weather = response.json()
        if current_weather:
            # Create a formatted string with essential weather details
            weather_summary = (
                f"Currently in Chennai :\n\n"
                f"Weather: {current_weather[0]['WeatherText']}\n"
                f"Actual Temperature (C): {current_weather[0]['Temperature']['Metric']['Value']}\n"
                f"Feels like (C): {current_weather[0]['RealFeelTemperature']['Metric']['Value']}\n"
                f"Wind Speed (Km/Hr): {current_weather[0]['Wind']['Speed']['Metric']['Value']}\n"
            )
            return weather_summary
        else:
            return "No weather data found."
    else:
        return f"Error: {response.status_code} - {response.text}"
def search_and_retweet():
    global retweet_count, next_reset_time

    # Reset the counter if it's a new day
    if datetime.now() >= next_reset_time:
        retweet_count = 0
        next_reset_time = datetime.now() + timedelta(days=1)
        print("Counter reset. Ready to retweet for the new day.")

    if retweet_count < RETWEET_LIMIT:
        for keyword in keywords:
            query = f"{keyword} -is:retweet lang:en"
            tweets = client.search_recent_tweets(query=query, tweet_fields=['id', 'text'], max_results=10)
            for tweet in tweets.data:
                if retweet_count >= RETWEET_LIMIT:
                    print("Retweet limit reached for today.")
                    return
                try:
                    print(f"Retweeting: {tweet.text}")
                    client.retweet(tweet.id)
                    retweet_count += 1
                    time.sleep(2)  # To avoid hitting rate limits
                except tweepy.TweepyException as e:
                    print(f"Error on retweet: {e}")
                except StopIteration:
                    break
    else:
        print("Retweet limit reached for today. Waiting until the next reset.")

# Function to generate a tweet
def generate_tweet(data):
    # Extracting relevant information
    headline = data['Headline']['Text']
    min_temp = data['DailyForecasts'][0]['Temperature']['Minimum']['Value']
    max_temp = data['DailyForecasts'][0]['Temperature']['Maximum']['Value']
    day_phrase = data['DailyForecasts'][0]['Day']['IconPhrase']
    night_phrase = data['DailyForecasts'][0]['Night']['IconPhrase']
    
    # Construct a tweet prompt
    tweet_prompt = (
        f"🌦️ WEATHER UPDATE FOR CHENNAI:\n"
        f"Prediction: {headline}\n"
        f"☀️ Day: {day_phrase}\n"
        f"🌡️ Temperature: {min_temp}°F to {max_temp}°F\n"
        f"🌃 Night: {night_phrase}\n\n"
        f"Update time : {datetime.now()}"
    )
    
    return tweet_prompt

def refine_tweet(prompt):
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=150, num_return_sequences=1, num_beams=5, early_stopping=True)
    generated_tweet = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_tweet

# Function to post a tweet
def post_tweet(tweet_text):
    try:
        tweet = tweet_text + "\n\n#ChennaiWeatherUpdates"
        
        response = client.create_tweet(text=tweet)
        print("Tweet posted successfully!")
        print("Response:", response)
    except TweepyException as e:
        print(f"An error occurred: {e}")

# Function to generate a meaningful weather summary
def generate_weather_summary(data):
    # Extracting relevant information
    headline = data['Headline']['Text']
    effective_date = data['Headline']['EffectiveDate']
    severity = data['Headline']['Severity']
    
    daily_forecast = data['DailyForecasts'][0]
    date = daily_forecast['Date']
    min_temp = daily_forecast['Temperature']['Minimum']['Value']
    max_temp = daily_forecast['Temperature']['Maximum']['Value']
    day_phrase = daily_forecast['Day']['IconPhrase']
    night_phrase = daily_forecast['Night']['IconPhrase']
    precipitation_type = daily_forecast['Night'].get('PrecipitationType', 'None')
    
    # Constructing the summary
    summary = (
        f"Weather Update for {date}:\n"
        f"Severity Level: {severity}\n"
        f"Daytime Weather: {day_phrase}, with temperatures ranging from {min_temp}°F to {max_temp}°F.\n"
        f"Nighttime Weather: Expect {night_phrase}, with {precipitation_type} expected.\n"
        f"Headline: {headline}\n"
        f"Effective Date: {effective_date}\n"
        f"For more details, visit: {data['Headline']['Link']}"
    )
    return summary

# def generate_ai_tweet(weather_response):
#     # Extracting relevant information from the JSON response
#     headline_text = weather_response['Headline']['Text']
#     effective_date = weather_response['Headline']['EffectiveDate']
#     temperature_min = weather_response['DailyForecasts'][0]['Temperature']['Minimum']['Value']
#     temperature_max = weather_response['DailyForecasts'][0]['Temperature']['Maximum']['Value']
#     day_icon_phrase = weather_response['DailyForecasts'][0]['Day']['IconPhrase']
#     night_icon_phrase = weather_response['DailyForecasts'][0]['Night']['IconPhrase']

#     # Creating a prompt for the model
#     prompt = (
#         f"Create a tweet with less than 120 characters about the weather alert: "
#         f"{headline_text}. Effective Date: {effective_date}. Temperature range: "
#         f"{temperature_min}°F to {temperature_max}°F. Day: {day_icon_phrase}, Night: {night_icon_phrase}."
#     )

#     # Load pre-trained model and tokenizer
#     model_name = "distilgpt2"
#     model = GPT2LMHeadModel.from_pretrained(model_name)
#     tokenizer = GPT2Tokenizer.from_pretrained(model_name)

#     # Encode the prompt
#     inputs = tokenizer.encode(prompt, return_tensors='pt')

#     # Generate text
#     outputs = model.generate(inputs, max_length=50, num_return_sequences=1)

#     # Decode the generated text
#     tweet = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     return tweet

# def generate_ai_tweet(weather_response):
#     # Extracting relevant information from the JSON response
#     headline_text = weather_response['Headline']['Text']
#     effective_date = weather_response['Headline']['EffectiveDate']
#     temperature_min = weather_response['DailyForecasts'][0]['Temperature']['Minimum']['Value']
#     temperature_max = weather_response['DailyForecasts'][0]['Temperature']['Maximum']['Value']
#     day_icon_phrase = weather_response['DailyForecasts'][0]['Day']['IconPhrase']
#     night_icon_phrase = weather_response['DailyForecasts'][0]['Night']['IconPhrase']

#     # Creating a prompt for the model
#     prompt = (
#         f"Create a tweet with less than 120 characters about the weather alert: "
#         f"{headline_text}. Effective Date: {effective_date}. Temperature range: "
#         f"{temperature_min}°F to {temperature_max}°F. Day: {day_icon_phrase}, Night: {night_icon_phrase}."
#     )

#     # Initialize textgenrnn and generate text
#     textgen = textgenrnn.TextgenRnn()
#     textgen.train_on_texts([prompt], num_epochs=1, gen_epochs=1)
#     generated_tweet = textgen.generate(return_as_list=True)[0]
    
#     return generated_tweet

tweet_count = 0
   
# Schedule the task
while tweet_count < 1:
    #tweet_text = get_min_update(API_KEY_MINUTES,LOCATION_COORDINATES)
    #print(tweet_text)
    #tweet_current = get_current_weather(API_KEY,LOCATION_KEY)
    #tweet = get_daily_update(API_KEY,LOCATION_KEY)
    daily = get_w_update(API_KEY_WEATHER,LOCATION_COORDINATES)
    #genT = generate_tweet(daily)
    genT = generate_daily_w(daily)
    # refined_tweet = refine_tweet(genT)
    # #textcontent = generate_w_tweet(tweet)
    # #post_tweet(tweet_current)
    # #post_tweet(refined_tweet)
    # #print(tweet)
    # print (daily)
    # print(genT)
    # print(refined_tweet)
    SAmple = "Test tweet from Rajesh"
    post_tweet(genT)
    tweet_count = tweet_count + 1;
