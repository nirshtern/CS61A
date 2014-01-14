"""Visualizing Twitter Sentiment Across America"""

from data import word_sentiments, load_tweets
from datetime import datetime
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait
from string import ascii_letters
from ucb import main, trace, interact, log_current_line


###################################
# Phase 1: The Feelings in Tweets #
###################################

# The tweet abstract data type, implemented as a dictionary.

def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as a Python dictionary.

    text  -- A string; the text of the tweet, all in lowercase
    time  -- A datetime object; the time that the tweet was posted
    lat   -- A number; the latitude of the tweet's location
    lon   -- A number; the longitude of the tweet's location

    >>> t = make_tweet("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_text(t)
    'just ate lunch'
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    >>> tweet_string(t)
    '"just ate lunch" @ (38, 74)'
    """
    return {'text': text, 'time': time, 'latitude': lat, 'longitude': lon}

def tweet_text(tweet):
    """Return a string, the words in the text of a tweet."""
    return tweet['text']

def tweet_time(tweet):
    """Return the datetime representing when a tweet was posted."""
    return tweet['time']

def tweet_location(tweet):
    """Return a position representing a tweet's location."""
    return (tweet['latitude'], tweet['longitude'])

# The tweet abstract data type, implemented as a function.

def make_tweet_fn(text, time, lat, lon):
    """An alternate implementation of make_tweet: a tweet is a function.

    >>> t = make_tweet_fn("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_text_fn(t)
    'just ate lunch'
    >>> tweet_time_fn(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> latitude(tweet_location_fn(t))
    38
    """
    def returner(word):    # a function that recevies a string(key) and returns a value, in a similar way to dictionary.
        if word=='text':
            return text
        if word=='time':
            return time
        if word=='lat':
            return lat
        if word=='lon':
            return lon
    return returner # Helper function is returned for selection of required data

def tweet_text_fn(tweet):
    """Return a string, the words in the text of a functional tweet."""
    return tweet('text')

def tweet_time_fn(tweet):
    """Return the datetime representing when a functional tweet was posted."""
    return tweet('time')

def tweet_location_fn(tweet):
    """Return a position representing a functional tweet's location."""
    return make_position(tweet('lat'), tweet('lon'))

### === +++ ABSTRACTION BARRIER +++ === ###

def tweet_words(tweet):
    """Return the words in a tweet."""
    return extract_words(tweet_text(tweet))

def tweet_string(tweet):
    """Return a string representing a functional tweet."""
    location = tweet_location(tweet)
    point = (latitude(location), longitude(location))
    return '"{0}" @ {1}'.format(tweet_text(tweet), point)

def extract_words(text):
    """Return the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    >>> extract_words('@(cat$.on^#$my&@keyboard***@#*')
    ['cat', 'on', 'my', 'keyboard']
    """
    separate = []  # a list to preserve the words after being seprated
    word = '' # a variable to hold current word before trasnferred into the seprate list

    for elem in text:    # A loop that goes through all characters in text and saves only words onto a list
        if elem not in ascii_letters:

            if word != '':
                separate.append(word)
            word = ''

        else:
             word += elem

    if word != '':  # special case: in case there is a word that wasn't appended in the last loop, we add it right after.
        separate.append(word)

    return separate

def make_sentiment(value):
    """Return a sentiment, which represents a value that may not exist.

    >>> positive = make_sentiment(0.2)
    >>> neutral = make_sentiment(0)
    >>> unknown = make_sentiment(None)
    >>> has_sentiment(positive)
    True
    >>> has_sentiment(neutral)
    True
    >>> has_sentiment(unknown)
    False
    >>> sentiment_value(positive)
    0.2
    >>> sentiment_value(neutral)
    0
    """
    #Chose to represent sentiment as a dictionary
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'
    return { 'sentiment': value }

def has_sentiment(s):
    """Return whether sentiment s has a value."""
    if s['sentiment'] == None:
        return False
    else: #(s['sentiment'] <= 1) or (s['sentiment'] >= -1):
        return True

def sentiment_value(s):
    """Return the value of a sentiment s."""
    assert has_sentiment(s), 'No sentiment value'
    return s['sentiment']

def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word.

    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    # Learn more: http://docs.python.org/3/library/stdtypes.html#dict.get
    return make_sentiment(word_sentiments.get(word))

def analyze_tweet_sentiment(tweet):
    """ Return a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.

    If no words in the tweet have a sentiment value, return
    make_sentiment(None).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("saying, 'i hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("berkeley golden bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """
    total_value, total_words = 0, 0

    #Separate all the words of tweet and iterate through them all
    for elem in tweet_words(tweet):        
        sentiment = get_word_sentiment(elem) #Convert word into a sentiment
        if has_sentiment(sentiment):    #If sentiment has a value, sum it up.
            total_value += sentiment_value(sentiment)
            total_words += 1
    
    #Case 1: Return a sentiment that is the average of all the sentiment values
    if total_words != 0:    
        return make_sentiment(total_value / total_words)

    #Case 2: Return a None sentiment if there were no words with sentiment values
    else:       
        return make_sentiment(None)


#################################
# Phase 2: The Geometry of Maps #
#################################

def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, use the latitude and longitude of its first
    position as its centroid.

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> round5 = lambda x: round(x, 5) # Rounds floats to 5 digits
    >>> tuple(map(round5, find_centroid(triangle)))
    (3.0, 2.0, 6.0)
    >>> tuple(map(round5, find_centroid([p1, p3, p2, p1])))
    (3.0, 2.0, 6.0)
    >>> tuple(map(float, find_centroid([p1, p2, p1])))  # A zero-area polygon
    (1.0, 2.0, 0.0)
    """

    #Helper function to calculate the area
    def area_point_calc(p1,p2):
        return (latitude(p1)*longitude(p2))-(latitude(p2)*longitude(p1))

    #Helper function to calculate the latitude of the centroid
    def lat_center(p1,p2):
        return (latitude(p1)+latitude(p2))*(latitude(p1)*longitude(p2)-latitude(p2)*longitude(p1))

    #Helper function to calculate the longitude of the centroid
    def lon_center(p1,p2):
        return (longitude(p1)+longitude(p2))*(latitude(p1)*longitude(p2)-latitude(p2)*longitude(p1))

    area=0
    i=0
    centroid_x=0
    centroid_y=0
    
    #Sum up all the areas, centroid_x and centroid_y values
    while i < len(polygon)-1:
        area        += area_point_calc(polygon[i],polygon[i+1])
        centroid_x  += lat_center(polygon[i],polygon[i+1])
        centroid_y  += lon_center(polygon[i],polygon[i+1])
        i           += 1

    area=area/2

    if area==0:
        centroid_x=latitude(polygon[0])
        centroid_y=longitude(polygon[0])

    #Finish calculating the final values of centroid_x and centroid_y
    else:
        centroid_x= centroid_x / (6 * area)
        centroid_y= centroid_y / (6 * area)

    return (centroid_x, centroid_y, abs(area))

def find_state_center(polygons):
    """Compute the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    http://en.wikipedia.org/wiki/Centroid#By_geometric_decomposition

    c_x = sum(c_xi * a_i) / sum(a_i)
    c_y = sum(c_yi * a_i) / sum(a_i)

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_state_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_state_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    centroid_x_sum, centroid_y_sum, area_sum = 0, 0, 0

    for elem in polygons:
        c_x, c_y, c_a = find_centroid(elem)  #Find the centroid of the polygon
        centroid_x_sum += c_x * c_a     #Sum c_xi * a_i
        centroid_y_sum += c_y * c_a     #Sum c_yi * a_i
        area_sum += c_a                 #Sum c_a

    #Compute the geographic center
    centroid_x_avg = centroid_x_sum / area_sum
    centroid_y_avg = centroid_y_sum / area_sum

    #Return the POSITION object!
    return make_position(centroid_x_avg, centroid_y_avg) 
    
###################################
# Phase 3: The Mood of the Nation #
###################################

def group_tweets_by_state(tweets):
    """Return a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("welcome to san francisco", None, 38, -122)
    >>> ny = make_tweet("welcome to new york", None, 41, -74)
    >>> two_tweets_by_state = group_tweets_by_state([sf, ny])
    >>> len(two_tweets_by_state)
    2
    >>> california_tweets = two_tweets_by_state['CA']
    >>> len(california_tweets)
    1
    >>> tweet_string(california_tweets[0])
    '"welcome to san francisco" @ (38, -122)'
    """
    states={}        
    for key in us_states:  # Creating a dictionary with states names as keys and their names as values 
        states[key]=find_state_center(us_states[key])

    tweets_by_state = {}

    for elem in tweets:  # A loop that runs through every tweet in 'tweets'
        closest = 4000 #Initializing closeset to distance larger than earth's radius   
        location = tweet_location(elem) # Saves the location of the tweet onto 'location'

        for value in states.values(): # A loop that runs through all the values of dictionary states and find which state center is closest to the tweet location
            current = geo_distance(location,value)
            if current<closest:
                closest=current
                center=value

        for key in states: # A loop that finds and saves the state name for the specific state center 
            if center == states[key]:
                state=key

        if state in tweets_by_state: # If the state exist in our dictionary we save the tweet under that state
            tweets_by_state[state].append(elem)

        else:                        # Else, we create a new key for the state and saves the tweet under that state
            tweets_by_state[state]=[elem]

    return tweets_by_state

def average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets
        ex: { state1 : [tweet1, tweet2, ...], state2: ...}
    
    NOTE: If state has no tweets with sentiment values, don't add it to dictionary.
    
    Steps: 
        1.) Iterate through the dictionary tweets_by_state
        2.) Average all the tweets of that state (if there are any)
        3.) Generate a new dictionary like so: { state: average sentiment, ... }
    """
    averaged_state_sentiments = {}

    #Average all the sentiment values of every tweet in the list tweets and return
    #the average sentiment value
    def average_tweets(tweets_list):
        sentiment_sum = 0
        sentiment_count = 0
        
        #Iterate through all the tweets and calculate their sentiment_sum & sentiment_count
        for t in tweets_list:
            #analyze_tweet_sentiment takes in a tweet, extracts all the words, and returns its calculated sentimenal value
            sentiment = analyze_tweet_sentiment(t) 
            
            #If sentiment has a value, sum it up!
            if has_sentiment(sentiment):
                sentiment_sum += sentiment_value(sentiment)
                sentiment_count += 1
        
        #Make a new sentiment and return it
        #If the state has at least one sentimental tweet, return a sentiment of the average
        if sentiment_count != 0:
            return make_sentiment (sentiment_sum / sentiment_count)
        
        #No sentimental tweets, so we return a None sentiment
        else:
            return make_sentiment (None)
    
    #Iterate through the tweets_by_state dictionary
    for state in tweets_by_state:         
        #state represents a list of tweets for the current state
        sentiment_of_state = average_tweets(tweets_by_state[state]) #Calculate the sentiment value of all the tweets in the state.        

        #If the state has a sentiment value, we are going to add two values to the averaged_state_sentiments dictionary
        #   1.) The state:                      state
        #   2.) The state's sentimental value:  sentiment_of_state
        #   key = state and value = sentiment_of_state
        if has_sentiment(sentiment_of_state):
            averaged_state_sentiments[state] = sentiment_value(sentiment_of_state)

        #If state doesn't have a sentiment value, don't add it to the dictionary!

    return averaged_state_sentiments



##########################
# Command Line Interface #
##########################

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores."""
    words = extract_words(text.lower())
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1:+}'
    for word in words:
        s = get_word_sentiment(word)
        if has_sentiment(s):
            print(layout.format(word, sentiment_value(s)))

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state."""
    us_centers = {n: find_state_center(s) for n, s in us_states.items()}
    center = us_centers[center_state.upper()]
    dist_from_center = lambda name: geo_distance(center, us_centers[name])
    for name in sorted(us_states.keys(), key=dist_from_center)[:int(n)]:
        draw_state(us_states[name])
        draw_name(name, us_centers[name])
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()

def draw_state_sentiments(state_sentiments):
    """Draw all U.S. states in colors corresponding to their sentiment value.

    Unknown state names are ignored; states without values are colored grey.

    state_sentiments -- A dictionary from state strings to sentiment values
    """
    for name, shapes in us_states.items():
        sentiment = state_sentiments.get(name, None)
        draw_state(shapes, sentiment)
    for name, shapes in us_states.items():
        center = find_state_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_query(term='my job'):
    """Draw the sentiment map corresponding to the tweets that contain term.

    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        s = analyze_tweet_sentiment(tweet)
        if has_sentiment(s):
            draw_dot(tweet_location(tweet), sentiment_value(s))
    wait()

def swap_tweet_representation(other=[make_tweet_fn, tweet_text_fn,
                                     tweet_time_fn, tweet_location_fn]):
    """Swap to another representation of tweets. Call again to swap back."""
    global make_tweet, tweet_text, tweet_time, tweet_location
    swap_to = tuple(other)
    other[:] = [make_tweet, tweet_text, tweet_time, tweet_location]
    make_tweet, tweet_text, tweet_time, tweet_location = swap_to


@main
def run(*args):
    """Read command-line arguments and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Trends")
    parser.add_argument('--print_sentiment', '-p', action='store_true')
    parser.add_argument('--draw_centered_map', '-d', action='store_true')
    parser.add_argument('--draw_map_for_query', '-m', action='store_true')
    parser.add_argument('--use_functional_tweets', '-f', action='store_true')
    parser.add_argument('text', metavar='T', type=str, nargs='*',
                        help='Text to process')
    args = parser.parse_args()
    if args.use_functional_tweets:
        swap_tweet_representation()
        print("Now using a functional representation of tweets!")
        args.use_functional_tweets = False
    for name, execute in args.__dict__.items():
        if name != 'text' and execute:
            globals()[name](' '.join(args.text))
