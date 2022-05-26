from checker import check
from test import get_test_data


class CommitMsgCorrector:
    def __init__(self, userID):
        self.user = userID
        self.commit_data = get_test_data()
        self.result = dict()

    def run(self):
        for msg in self.commit_data[:30]:
            check(msg)
