import pandas as pd


def get_test_data():
    data = pd.read_csv('./data/output/commit_data.csv')
    commit_data = data['commit message']

    return commit_data.tolist()
