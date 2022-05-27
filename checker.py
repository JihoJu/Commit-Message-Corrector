import json
import re
import os
from google.cloud import language_v1
from collections import OrderedDict

DEFAULT_SUBJECT_LIMIT = 50
DEFAULT_BODY_LIMIT = 72
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


def check(message):
    """ Check if a commit message is good or bad based on commit message convention

        - check_type_is_specified()
            commit message subject 에 commit type 을 포함 여부 및 이후 문장이 명령형 판단을 위해 commit type 을 제거한
            commit message 를 리턴 받음.
        - check_type_in_bracket()
            commit message subject 에 bracket 안 어느 type 포함 여부 확인 ex) [DevTools], 이후 명령형 문장인 지 판단을 위해
            bracket 부분을 제외한 commit message 를 리턴 받는다.

        :param message: A commit message
        :return:
    """
    res = OrderedDict()

    # subject_type_is_specified & subject_type_in_bracket 정보 dict 에 넣기 위함
    res["subject_type_is_specified"] = False
    res["subject_type_in_bracket"] = False

    # Git 에서 자동 생성된 commit, 숫자만 있는 case, 빈 commit message, commit message 글자 수 1개 이하 case -> 쓰레기 data 분류
    if auto_commit_judge(message) or trash_commit_judge(message):
        res["invalid_commit_message"] = 1
        return  # 이런 msg 도 분류 작업이 필요
    res["subject_is_separated_from_body"] = check_subject_is_separated_from_body(message)
    res["subject_is_not_too_long"] = check_subject_is_not_too_long(message, DEFAULT_SUBJECT_LIMIT)
    res["subject_does_not_end_with_punctuation"] = check_subject_does_not_end_with_punctuation(message)
    # commit message subject 에 commit type 을 포함 여부 확인
    if check_type_is_specified(message):
        res["subject_type_is_specified"] = True
        parsed_message = check_type_is_specified(message)
    # commit message subject 에 bracket 안 어느 type 포함 여부 확인 ex) [DevTools]
    elif check_type_in_bracket(message):
        res["subject_type_in_bracket"] = True
        parsed_message = check_type_in_bracket(message)
    else:  # commit message 가 다음 case 에 포함되지 않는 경우 (1. commit type, 2. Type in Bracket)
        parsed_message = message
    res["subject_uses_imperative"] = check_subject_uses_imperative(parsed_message)  # commit message 가 명령문인 지 확인
    res["check_subject_is_capitalized"] = check_subject_is_capitalized(parsed_message)
    res["body_lines_are_not_too_long"] = check_body_lines_are_not_too_long(message, DEFAULT_BODY_LIMIT)

    return res


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


def check_subject_is_separated_from_body(message):
    """ Check if subject is separated from body

        :param message: A commit message
        :return check_result: subject 와 body 가 분리되어 있으면 True or not True (False)
    """
    lines = message.splitlines()
    if len(lines) > 1:
        # The second line should be empty
        check_result = not lines[1]
    else:
        # If there is just one line then this rule doesn't apply
        check_result = True

    return check_result


def check_subject_is_not_too_long(message, subject_limit):
    """ Check if subject is too long

        :param message: A commit message
        :param subject_limit: Limited number of characters for subject
        :return check_result: 50자를 넘지 않으면 True or not Ture (False)
    """
    lines = message.splitlines()
    check_result = len(lines[0]) <= subject_limit

    return check_result


def check_body_lines_are_not_too_long(message, body_limit):
    """ Check if body is too long

        :param message: A commit message
        :param body_limit: Limited number of characters for body
        :return check_result: 72자를 넘지 않으면 True or not Ture (False)
    """
    lines = message.splitlines()
    check_result = True
    for line in lines:
        if len(line) > body_limit:
            check_result = False
            break

    return check_result


def check_subject_does_not_end_with_punctuation(message):
    """ Check if subject ends with period

        :param message: A commit message
        :return check_result: subject 마지막 문자가 punctuation 이 아닌 경우 True / 맞다면 False
    """
    punctuation_pattern = re.compile(r'[!.?](?:\s+)?$(?<=)')

    lines = message.splitlines()
    check_result = not punctuation_pattern.match(lines[0][-1])

    return check_result


def check_type_is_specified(message: str):
    """ Determine if the commit message contains the specified commit type

        :param message: A commit message
        :return: 특정 commit type 이 있다면 해당 type 이 제거된 string
    """
    sub_type_msg = None

    commit_type_list = ["feat:", "fix:", "design:", "build:", "chore:", "ci:", "docs:", "style:", "refactor:", "test:",
                        "rename:", "remove:", "perf"]

    type_regex = r'[A-Za-z]*(\(.*\)|\s-\s.*)?:'
    type_pattern = re.compile(type_regex)  # solution:, feat(test.py): etc 정규식
    res = type_pattern.match(message)

    if res is not None and res.start() == 0:  # commit type 정규식 표현이 존재 + 위치가 맨 앞
        scope_regex = r'\(.*\)|\s-\s.*'  # feat(test.py): 에서 (test.py) 를 제거
        commit_message = re.sub(scope_regex, '', res.string)
        commit_message = commit_message.split()
        # 특정 type 이 아닌 경우 False 를 리턴
        # -> 처리 예정) solution: 등 회사, 자기가 구별 가능 type 을 쓸 경우도 따로 생각해두자(이 경우 권장을 해주는 방향)
        # ex) 이런 type 은 어떤가요??
        sub_type_msg = re.sub(type_regex, '', message).strip() if commit_message[0] in commit_type_list else None

    return sub_type_msg


def check_type_in_bracket(message: str):
    """ Determine if the type enclosed in the bracket exists in front of the commit message
        ex)
            [DevTools] Fix regex for formateWithStyles function
            [DevTools][Bug] Fix regex for documents

        :param message: A commit message
        :return sub_bracket_msg: bracket 으로 wrapped type 이 있다면 이를 제거한 commit message (string)
    """

    bracket_regex = r'(\[[A-Za-z]*\])+'
    pattern = re.compile(bracket_regex)
    res = pattern.match(message)

    sub_bracket_msg = re.sub(bracket_regex, '', message).strip() if res else None

    return sub_bracket_msg


def check_subject_uses_imperative(message: str):
    """ Determine if a commit message's mood is imperative

        Follow the following rules
            - message 를 모두 소문자로 변경
            - 정확도 향상을 위해 you + message 로 구문 분석을 진행
            - 첫 번째 토큰(word) 가 부사일 경우 두 번째 토큰(word) 를 token 으로 지정
                - "fix: correctly fix ~~" 와 같은 commit message 를 고려
            - token 이 동사인 경우
                - 3인칭 동사: runs, presents, fixes etc
                - 과거형 동사: fixed, updated etc
                2가지 case 를 고려

        :param message: A commit message
        :return:
    """
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language = "en"
    # 2인칭 주어 you 로 정확도 상향 (그것도 엄청!)
    document = {"content": "you " + message.lower(), "type_": type_, "language": language}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_syntax(request={'document': document, 'encoding_type': encoding_type})
    token = response.tokens[1]  # index 0 은 you

    # 첫 번째 token 이 부사인 경우를 고려 ex) fix: correctly fix ~~
    token = response.tokens[2] if language_v1.PartOfSpeech.Tag(token.part_of_speech.tag).name == "ADV" else token

    part_of_speech = token.part_of_speech
    if language_v1.PartOfSpeech.Tag(part_of_speech.tag).name != "VERB":
        return False, "NO"
    else:
        if language_v1.PartOfSpeech.Tense(part_of_speech.tense).name == "PAST":
            return False, "PAST"
        if language_v1.PartOfSpeech.Person(part_of_speech.person).name == "THIRD":
            return False, "THIRD"

    return True, "IMPERATIVE"


def check_subject_is_capitalized(message: str):
    """ Check if commit message subject is capitalized

        :param message: A commit message
        :return check_result: subject is capitalized True / or not True (False)

    """
    lines = message.splitlines()
    # Check if first character is in upper case
    check_result = lines[0][0].isupper()

    return check_result
