import codecs
import csv
import json
import os
import sys
import urllib.parse as urlParse
import urllib.request as urlRequest
import math
from graphqlclient import GraphQLClient

apiVersion = 'alpha'
authTokenPath = os.path.join(os.getcwd(),"auth_token")
client = GraphQLClient('https://api.smash.gg/gql/' + apiVersion)
with open(authTokenPath, 'r') as authFile:
	client.inject_token('Bearer ' + authFile.readline())

def retrievePowerRankingData():
	data = []
	url='https://braacket.com/league/shieldpoke/ranking/E65F50BF-5218-4B0F-B6CC-B4F11BDD92A2?rows=200&cols=&page=1&page_cols=1&game_character=&country=&search=&export=csv&hash=3e2e863ef8e7e0f5db6c38df4e6899fe'
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
	req = urlRequest.Request(url, headers = headers)
	x = urlRequest.urlopen(req)
	csvValue = x.read().decode('utf-8')
	csvReader = csv.DictReader(csvValue.splitlines())	
	[data.append(rows) for rows in csvReader]
	return [ (player['Player'],player['Points']) for player in data]

def savePowerRankingDataAsJSON():
	with open(os.path.join(os.getcwd(),'seeding.json'),'w') as jsonFile:
		jsonFile.write(json.dumps(powerRankingData, ensure_ascii=False, indent=4))

def retrieveEntrantNames(slug):
	eventStandings = client.execute('''query EventStandings($slug: String!) {
		tournament(slug: $slug){
				name,
				events{
					phases {
						name,
						id
					}
				}
			}
		}''',{
	"slug":slug
	})
	eventStandingsData = json.loads(eventStandings)
	top32ID = [phase['id'] for phase in eventStandingsData['data']['tournament']['events'][0]['phases'] if phase['name']=='Top 32'][0]
	seeding = client.execute('''query GetSeeding($id: ID!) {	
			phase(id: $id) {
				seeds(query:{
					page: 1
					perPage: 32
				})
				{
				nodes{
					entrant{
            			name						
					}
				}
     		 }
		}
  	}''',{
		"id":top32ID
		})
	seedingData = json.loads(seeding)
	return [nodes['entrant']['name'] for nodes in seedingData['data']['phase']['seeds']['nodes']]

powerRankingData = retrievePowerRankingData()
entrants = retrieveEntrantNames(sys.argv[1])
entrantsFromPR = []
for player in powerRankingData:
	for entrant in entrants:
		if player[0] in entrant:
			entrantsFromPR.append(player)
		if entrant in player[0]:
			entrantsFromPR.append(player)
entrantsFromPR = list(dict.fromkeys(entrantsFromPR))
print(entrantsFromPR)
scores = [int(playerData[1],10) for playerData in entrantsFromPR]
maxScore = max(scores)
minScore = min(scores)
scoreGap = maxScore - minScore
entrantsSkill = [[playerData[0], 6+math.floor(10*(int(playerData[1],10) - maxScore + minScore)/scoreGap)] for playerData in entrantsFromPR]
print(entrantsSkill)