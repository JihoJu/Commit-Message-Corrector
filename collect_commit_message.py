import pandas as pd
import github
from github import Github
import sys


def get_github_username():
    res = []
    data = pd.read_csv('./data/input/github_id_data.csv', delimiter='\t')
    for d in data['id']:
        res.append(d)

    return res


class GitHubAPIShell:
    """ GitHub API 객체

    - pyGithub 라이브러리 사용
    - token 이 필요!! : 만약 token 과 함께 Github 객체 호출 시 id or IP 당 1시간에 60번 밖에 호출을 못함
    """

    def __init__(self):
        self.user = None  # GitHub user 객체 담기 위함
        self.data = pd.DataFrame(columns=["commit message"])

    def run(self):
        g = Github(login_or_token="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")

        usernames = get_github_username()  # csv 파일에 저장된 github username 들을 가져온다.
        for user in usernames:
            self.user = g.get_user(user)  # id 넣어야 함
            self.get_repo_info()

        self.data.to_csv('./data/output/commit_data.csv', index=False)  # commit message data 를 csv 에 저장

        return 0

    def get_repo_info(self):
        """ Github user 의 repo 객체를 호출
        """
        repos = self.user.get_repos()

        for repo in repos:  # user repo 5개만 commit API 를 호출
            self.get_commits(repo)

    def get_commits(self, repo):
        """ Github commit API 호출

            :param repo: Repository Object
        """

        try:
            for commit in repo.get_commits():
                commit_message = " ".join(commit.commit.message.split())
                self.data.loc[len(self.data)] = commit_message
        except github.GithubException as e:
            print(repo.full_name, e)


def main():
    return GitHubAPIShell().run()


if __name__ == '__main__':
    sys.exit(main())
