import logging
import time
from glob import glob
from typing import List, Optional

from git import Repo

from .parser import (
    CloneProgress,
    get_remote_latest_commit,
    init_git,
    read_config,
)

logger = logging.getLogger(__name__)


class EventController:
    _types = ("dev", "master")

    def __init__(self, path_to_ini: Optional[str] = None):
        self._config = read_config(path_to_ini=path_to_ini)

    @property
    def config(self):
        return self._config

    def clone_repo(self, repo_url: str, dir_type: str) -> None:
        """
        Clone repository from github/gitlab/gitea...

        :param repo_url: Git repository url(ssh/https)
        :param dir_type: Directory type (master/dev)
        """
        logger.info("Cloning the repository {repo}".format(repo=repo_url))
        Repo.clone_from(
            url=repo_url,
            to_path=self._config["directories"][dir_type],
            progress=CloneProgress(),
        )

    def _handle_repositories(self, type_: str) -> None:
        _dirs: List[str] = glob(self._config["directories"][type_] + "/.*")
        repo_url: Optional[str] = self._config["git"].get("url")

        if repo_url is None:
            raise Exception

        if len(_dirs) == 0:
            self.clone_repo(repo_url=repo_url, dir_type=type_)

    def _parse_repositories(self, type_: str) -> None:
        """
        Check the dirs. for .git directory
        :return:
        """
        _repo = init_git(self._config["directories"][type_])
        branches: List[str] = [
            branch for branch in _repo.git.branch().split() if branch != "*"
        ]

        if self._config["branches"][type_] not in branches:
            _repo.git.checkout("HEAD", b=self._config["branches"][type_])

        _repo.git.checkout(self._config["branches"][type_])

        logger.info("Pulling the updates")
        logger.info(
            _repo.git.branch(
                "--set-upstream-to=origin/" + self._config["branches"][type_],
                self._config["branches"][type_],
            )
        )
        try:
            logger.info(
                _repo.git.reset("--hard", "HEAD~")
            )  # for prevent merge conflicts
            logger.info(_repo.git.pull())
        except Exception as e_info:
            print(e_info)

    def _get_latest_commit(self, git_path: str, type_: str) -> str:
        """
        Get latest local branch's commit
        :param git_path: Path to repo
        :return: Hash of local repo commit
        """
        repo = init_git(git_path)
        repo.git.checkout(type_)
        sha = repo.head.object.hexsha

        return sha

    def handle_new_commit(self, type_: str) -> bool:
        current_commit_hash = self._get_latest_commit(
            git_path=self._config["directories"][type_], type_=type_
        )
        remote_branch_commit_hash = get_remote_latest_commit(
            repo_path=self._config["directories"][type_],
            git_url=self._config["git"]["url"],
            branch=self._config["branches"][type_],
        )

        if current_commit_hash == remote_branch_commit_hash:
            return False
        return True


class PyCD(EventController):
    def __init__(self, path_to_ini: Optional[str] = None):
        super().__init__(path_to_ini)

    def continuous_delivering(self, retry_time: Optional[float] = None) -> None:
        """
        Start continuous delivering process
        :param retry_time: Time between getting updates
        """
        if retry_time is None:
            retry_time = 10

        logger.info("[x] Starting the continuous delivering. To exit press CTRL+C")

        while True:
            for branch_type in self._types:
                self._handle_repositories(type_=branch_type)
                is_new_commit = self.handle_new_commit(type_=branch_type)

                if not is_new_commit:
                    continue

                logger.info(
                    "Detected new commit at {branch}".format(branch=branch_type)
                )
                self._parse_repositories(type_=branch_type)

            time.sleep(retry_time)
