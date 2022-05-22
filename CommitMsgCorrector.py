import bad_commit_message_blocker_sample


class CommitMsgCorrector:
    def __init__(self, userID, commit_msg: list):
        self.user = userID
        self.commit_data = commit_msg
        self.result = dict()

    def run(self):
        for msg in self.commit_data:
            bad_commit_message_blocker_sample.check(msg)
