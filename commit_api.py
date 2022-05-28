import requests
import json

# Setting Header
headerDict = {}
headerDict.setdefault('Authorization','Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI2OTAwNDY3NSIsImF1dGgiOiJST0xFX1VTRVIiLCJleHAiOjE2NTM3MzA0NTV9.nFenOSLG21yF1UKtTtuCZvMuX8COla3XvLMHKH7BivK-qFsL7CBdHQ9eqiLrXq4-jw29pUp4kEtQ5RVY6VAn5A')
url = 'http://3.35.212.150:8080/get-user-commit-data'

# Request
def get_commit_data():
    requestData = requests.get(url, headers=headerDict)
    text = requestData.text
    data = json.loads(text)

    return data  

if __name__ == '__main__': 
    get_commit_data()
