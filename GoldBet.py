# Import requests library to make HTTP requests
import requests
# Import sqlite3 library
import sqlite3
import json
from flask import Flask, render_template

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = 'your_odds_api_key'

SPORT = 'soccer' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'eu' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'decimal' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        'api_key': API_KEY
    }
)


if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    print('List of in season sports:', sports_response.json())

# # # # # # # # 

odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
)

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    print(odds_json)

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

app = Flask(__name__)

def find_arbitrage_opportunities(odds_json):
    opportunities = []
    for event in odds_json:
        # Check if market information is available for this event
        if 'markets' in event:
            # Get the best home and away odds
            best_home_odds = max([market['outcomes'][0]['price'] for market in event['markets']])
            best_away_odds = max([market['outcomes'][1]['price'] for market in event['markets']])
            
            # Calculate the implied probabilities
            implied_home_prob = 1 / best_home_odds
            implied_away_prob = 1 / best_away_odds
            
            # Check if there is an arbitrage opportunity
            if implied_home_prob + implied_away_prob < 1:
                # Arbitrage opportunity found!
                opportunities.append({'event': event['teams'], 'odds': [best_home_odds, best_away_odds]})
            
    return opportunities

@app.route('/')
def index():
    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }
    )

    if odds_response.status_code != 200:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
        return "Error getting odds"

    else:
        odds_json = odds_response.json()
        arbitrage_opportunities = find_arbitrage_opportunities(odds_json)
      

    # Print the arbitrage opportunities
        print(arbitrage_opportunities)
        return render_template('index.html', opportunities=arbitrage_opportunities)
    

if __name__ == '__main__':
    app.run()