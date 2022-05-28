from checker import check
from test import get_test_data


class CommitMsgCorrector:
    def __init__(self, userID):
        self.user = userID
        self.commit_data = get_test_data()
        self.result = dict()

    def run(self):
        for commit_message in self.commit_data:
            self.result[commit_message] = check(commit_message)

        for result in self.result.items():
            print(result)


aa = CommitMsgCorrector("a")
aa.run()
