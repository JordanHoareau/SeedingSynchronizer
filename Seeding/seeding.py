import codecs
import csv
import json
import os
import sys
import urllib.parse as urlParse
import urllib.request as urlRequest
from graphqlclient import GraphQLClient

apiVersion = 'alpha'
authTokenPath = os.path.join(os.getcwd(),"auth_token")
client = GraphQLClient('https://api.smash.gg/gql/' + apiVersion)
with open(authTokenPath, 'r') as authFile:
	client.inject_token('Bearer ' + authFile.readline())

def retrievePowerRankingData():
	data = []
	url='https://braacket.com/league/shieldpoke/ranking/34366887-9130-474A-97D7-5A80143865D2?rows=200&cols=&page=1&page_cols=1&game_character=&country=&search=&export=csv&hash=0bf978e9bc000a9c7e432db0e3c07c18'
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
	req = urlRequest.Request(url, headers = headers)
	x = urlRequest.urlopen(req)
	csvValue = x.read().decode('utf-8')
	csvReader = csv.DictReader(csvValue.splitlines())	
	[data.append(rows) for rows in csvReader]
	return data

def savePowerRankingDataAsJSON():
	path = "C:\\Users\\jhoareau\\Desktop\\Seeding"
	with open(os.path.join(path,'seeding.json'),'w') as jsonFile:
		jsonFile.write(json.dumps(powerRankingData, ensure_ascii=False, indent=4))

def retrieveTournamentData(slug):
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
	print(eventStandingsData['data']['tournament']['events'][0]['phases'])
	top32ID = [phase['id'] for phase in eventStandingsData['data']['tournament']['events'][0]['phases'] if phase['name']=='Top 32'][0]
	print(top32ID)
	result = client.execute('''query GetEventID($slug: String!) {
		tournament(slug: $slug){
			name,
			events{
			phases {
				name,
				seeds(query:{
				page: 1
				perPage: 60
				})
				{
				nodes{
					id
					seedNum
					entrant{
					id
					participants{
						id
						gamerTag
					}
					}
				}
				}
			}
			}
		}
		}''',{
		"slug":slug
		})
	return result
	

powerRankingData = retrievePowerRankingData()
tournamentData = retrieveTournamentData(sys.argv[1])
