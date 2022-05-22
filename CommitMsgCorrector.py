import json
import os
from google.cloud import language_v1
import bad_commit_message_blocker_sample
import test

secret_file = "./secrets.json"

with open(secret_file) as f:
    secrets = json.loads(f.read())


def get_secret(setting):
    """ 비밀 변수를 가져오거나 명시적 예외를 반환
    """
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise print(error_msg)


credential_path = get_secret("GCP_SECRET_PATH")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


class CommitMsgCorrector:
    def __init__(self, userID):
        self.user = userID
        self.commit_data = test.get_test_data()
        self.result = dict()

    def run(self):
        for msg in self.commit_data[:5]:
            if auto_commit_judge(msg) or trash_commit_judge(msg):
                continue  # 이런 msg 도 분류 작업이 필요
            analyze_syntax("you " + msg.lower())  # 2인칭 주어 you 로 정확도 상향 (그것도 엄청!)


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


def analyze_syntax(message):
    res = []

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": message, "type_": type_, "language": language}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_syntax(request={'document': document, 'encoding_type': encoding_type})

    print(response)