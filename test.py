import pandas as pd
from commit_api import get_commit_data


def get_test_data():
  data = get_commit_data()
  
  commit_list = []
  for i in range(len(data)):
    commit_data = data[i]['commitDAOS']
    if len(commit_data) > 0:
      commit_list.append(commit_data[0]['message'])

  return commit_list



if __name__ == '__main__': 
    get_test_data()
