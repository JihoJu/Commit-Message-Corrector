import bad_commit_message_blocker_sample
import test


class CommitMsgCorrector:
    def __init__(self, userID):
        self.user = userID
        self.commit_data = test.get_test_data()
        self.result = dict()

    def run(self):
        for msg in self.commit_data:
            bad_commit_message_blocker_sample.check(msg)


def trash_commit_judge(message):
    if message.isdigit():
        return True
    elif message is None:
        return True
    elif len(message) <= 1:
        return True

    return False


def auto_commit_judge(message):
    if message.find('Merge pull request #') != -1:
        return True
    elif message.find("Merge branch '") != -1:
        return True

    return False
