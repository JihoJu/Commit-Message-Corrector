import json
import re
import os
from google.cloud import language_v1
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
        for msg in self.commit_data[:7]:
            check(msg)


def check(message):
    """ Check if a commit message is good or bad based on commit message convention

        :param message: A commit message
        :return:
    """
    if auto_commit_judge(message) or trash_commit_judge(message):
        return  # 이런 msg 도 분류 작업이 필요
    analyze_syntax("you " + message.lower())  # 2인칭 주어 you 로 정확도 상향 (그것도 엄청!)


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


def check_type_is_specified(commit_type):
    commit_type_list = ["feat:", "fix:", "design:", "build:", "chore:", "ci:", "docs:", "style:", "refactor:", "test:",
                        "rename:", "remove:", "perf", "solution"]
    if commit_type in commit_type_list:
        return True

    return False


def check_type_in_bracket(commit_type):
    pattern = re.compile(r'\[[A-Za-z]*\]')

    try:
        res = pattern.match(commit_type)
    except res is None:
        return False

    return True


def check_subject_uses_imperative(token):
    """
        Token (word) 가 동사, 시제(과거형, 현재), 3인칭 동사(runs, adds, etc) 인지를 판별

        :param token: language_v1.Token Object
        :return:
    """

    part_of_speech = token.part_of_speech
    if language_v1.PartOfSpeech.Tag(part_of_speech.tag).name != "VERB":
        print("동사 아님")
        return False
    else:
        if language_v1.PartOfSpeech.Tense(part_of_speech.tense).name == "PAST":
            print("과거형")
            return False
        if language_v1.PartOfSpeech.Person(part_of_speech.person).name == "THIRD":
            print("3인칭 동사", token.text)
            return False
    return True


def analyze_syntax(message: str):
    """

    :param message: you + commit message
        ex) message: you feat: add document
    :return:
    """
    res = []

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": message, "type_": type_, "language": language}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_syntax(request={'document': document, 'encoding_type': encoding_type})
    tokens = response.tokens
    """
        check_type_is_specified() 함수 인자: feat 과 : 를 합친 string 값
        ex) message: you feat: add document
    """
    if tokens[1].text.content == '[' and check_type_in_bracket("".join(map(lambda x: x.text.content, tokens[1:4]))):
        print(response.sentences[0].text.content)
    if check_type_is_specified("".join(map(lambda x: x.text.content, tokens[1:3]))):
        print(response.sentences[0].text.content)
    if check_subject_uses_imperative(tokens[1]):
        print("확인")


aa = CommitMsgCorrector("aa")
aa.run()
