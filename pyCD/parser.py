import configparser
import os
import shutil
from pathlib import Path
from typing import Optional

from git import RemoteProgress, Repo

from pyCD.exceptions import NotCompleteSetupFile

ROOT_DIR = Path().resolve()


class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        if message:
            print(message)


def get_repo_url(path_to_ini: Optional[str] = None) -> Optional[str]:
    """
    Get github repository url from provided url or .git directory of project
    :param path_to_ini: Path to setup file dir.
    :return: Github repo. url or None if .git dir. is not correct
    """
    if path_to_ini is None:
        path_to_ini = os.path.join(ROOT_DIR, "pycd.ini")

    config = configparser.ConfigParser()
    config.read(path_to_ini)

    return config["git"].get("url")


def read_config(path_to_ini: Optional[str] = None):
    """
    Read .ini setup file of pyCD
    :param path_to_ini: Path to pycd.ini setup file
    """
    if path_to_ini is None:
        path_to_ini = os.path.join(ROOT_DIR, "pycd.ini")

    config = configparser.ConfigParser()
    config.read(path_to_ini)  # Read file

    if "branches" not in config.sections():
        raise NotCompleteSetupFile(
            "No `branches` section in {ini}".format(ini=path_to_ini)
        )

    if "directories" not in config.sections():
        raise NotCompleteSetupFile(
            "No `directories` section in {ini}".format(ini=path_to_ini)
        )

    if "git" not in config.sections():
        raise NotCompleteSetupFile("No `git` section in {ini}".format(ini=path_to_ini))

    dev_branch = config["branches"].get("dev")
    master_branch = config["branches"].get("master")

    dev_path = config["directories"].get("dev")
    master_path = config["directories"].get("master")

    git_url = config["git"].get("url")

    return {
        "directories": {"dev": dev_path, "master": master_path},
        "branches": {"dev": dev_branch, "master": master_branch},
        "git": {"url": git_url},
    }


def init_git(repo_path: str) -> Repo:
    """
    Initialize git repo
    :param repo_path: Path to directory
    """
    repo = Repo(os.path.join(repo_path, ".git"))
    return repo


def get_remote_latest_commit(
    git_url: str, branch: str, repo_path: str
) -> Optional[str]:
    """
    Get last commit from remote branch
    :param git_url: Remote repo. url
    :param branch: Branch name
    :param repo_path: Location path
    :return: Hash of commit
    """
    _repo_path = Path(repo_path + "_local")

    try:
        repo = Repo.clone_from(git_url, _repo_path, depth=1, branch=branch)
        sha = repo.head.object.hexsha
        shutil.rmtree(_repo_path)

        return sha

    except Exception as e_info:
        print(e_info)
        shutil.rmtree(_repo_path)
        return None
