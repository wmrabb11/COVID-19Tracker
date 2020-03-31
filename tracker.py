#!/usr/bin/env python3

# @author: Will Rabb
# @date: 03/31/2020
# Python CLI tool to view COVID-19 stats

# DISCLAIMER: API data is provided by 'TrackCorona'
# Website: https://www.trackcorona.live/

# DISCLAIMER: US State Dictionary provided by user 'rogerallen' on GitHubGist
# Website: https://gist.github.com/rogerallen/1583593

###########
# Imports #
###########
import argparse
import json
import requests
import us_dict

#############
# Constants #
#############
BASE_URL = 'https://www.trackcorona.live/api/'

###########
# Helpers #
###########
def print_stats(scope, confirmed, dead, recovered):
    if not confirmed:
        confirmed = 0
    if not dead:
        dead = 0
    if not recovered:
        recovered = 0
    print( f'-----{scope.upper()} COVID-19 Stats-----' )
    print( f'[*] # of confirmed cases: {confirmed:,}' )
    print( f'[+] # recovered: {recovered:,}' )
    print( f'[-] # dead: {dead:,}' )
    print( f'[*] # active: {confirmed - (recovered + dead):,}' )
    print( f'[+] Recovery rate: {recovered / confirmed * 100:.2f}%' )
    print( f'[-] Mortality rate: {dead / confirmed * 100:.2f}%' )

def make_request(scope='countries'):
    r = requests.get(BASE_URL + scope)
    resp = None
    try:
        resp = json.loads(r.content)
    except Exception:
        print( '[-] The API is currently being updated. Please check again soon.' )
        return
    if resp['code'] != 200:
        code = resp['code']
        print( f'[-] The API request failed with code {code}' )
        return None
    return resp['data']

###############
# Fetch Stats #
###############
def global_stats():
    data = make_request()
    if not data:
        return False
    confirmed = sum([d['confirmed'] for d in data])
    dead = sum([d['dead'] for d in data])
    recovered = sum([d['recovered'] for d in data])
    print_stats('global', confirmed, dead, recovered)
    return True

def country_stats(country):
    data = make_request()
    if not data:
        return False
    for d in data:
        if d['location'].lower() == country.lower():
            print_stats(country, d['confirmed'], d['dead'], d['recovered'])
            return True
    print( f'[-] Could not find results for {country}' )
    return False

def state_stats(state):
    data = make_request('cities')
    if not data:
        return False
    full_state = us_dict.abbrev_us_state[state]
    confirmed = sum([d['confirmed'] if full_state in d['location'] else 0 for d in data])
    dead = sum([d['dead'] if full_state in d['location'] else 0 for d in data])
    recovered = sum([d['recovered'] if d['recovered'] and full_state in d['location'] else 0 for d in data])
    print_stats(full_state, confirmed, dead, recovered)
    return True

def county_stats(county, state):
    data = make_request('cities')
    if not data:
        return False
    full_state = us_dict.abbrev_us_state[state]
    for d in data:
        if full_state.lower() in d['location'].lower() and county.lower() in d['location'].lower():
            print_stats(f'{county} County, {full_state}', d['confirmed'], d['dead'], d['recovered'])
            return True
    print( f'[-] Could not find results for {county} County, {full_state}' )
    return False

##############
# Main Logic #
##############
if __name__=="__main__":
    examples = '''Examples:
        ./tracker.py -s global
        ./tracker.py -s country -C "United States"
        ./tracker.py -s state -S NY
        ./tracker.py -s county -c columbia -S NY'''
    parser = argparse.ArgumentParser(description='CLI tool written in Python3 to track COVID-19 statistics', 
            epilog=examples,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--scope', choices=['global','country','state','county'], 
            help='Specify if you want to view global, country, state, or county-specific data', 
            required=True)
    parser.add_argument('-C', '--country', help='The country to view data for (required for scope=country)')
    parser.add_argument('-S', '--state', help='The 2 letter code of the state to view data for (required for scope=state and scope=county)')
    parser.add_argument('-c', '--county', help='The county to view data for (required for scope=county)')
    args = parser.parse_args()

    if args.scope == 'global':
        global_stats()
    elif args.scope == 'country' and args.country:
        country_stats(args.country)
    elif args.scope == 'state' and args.state and len(args.state) == 2:
        state_stats(args.state)
    elif args.scope == 'county' and args.county and args.state and len(args.state) == 2:
        county_stats(args.county, args.state)
    else:
        parser.print_help()
