#!/usr/bin/python3
# SPDX-License-Identifier: MIT

"""Provide git toolbox helper functions to manage git repositories at
scale on your local workstation, for keeping the track of them and let you
focus which repositories need some attention.
"""
import sys
import os
import argparse
import logging
import subprocess

from datetime import datetime
import yaml


WORKSPACE = os.environ.get("WORKSPACE", os.path.join(os.environ["HOME"], "workspace"))
_ARGS = None


# pylint: disable=R0903
class _:
    """Encapsulate the constants"""

    PROG = "git-tb"
    KEY_CWD = "cwd"
    KEY_CONTEXT = "context"
    GIT = "git"
    HIDDEN_GIT = ".git"
    UTF_8 = "utf-8"
    # Environment variable with the ordered list of priorities for upstream
    # in the workspace; by default is set to
    # "upstream,origin" => ['upstream', 'origin']
    ENV_GIT_REMOTES = "GIT_REMOTES"
    GIT_REMOTES_DEFAULT = "upstream,origin"

    WORKSPACE_FILE = "workspace.yaml"

    # os.walk return dirpath on index 0
    WALK_DIRPATH = 0
    # os.walk return dirnames on index 1
    WALK_DIRNAMES = 1
    # os.walk return filenames on index 2
    WALK_FILENAMES = 2

    # Subcommands
    SUBCMD_LIST = "list"
    SUBCMD_CHECK = "check"
    SUBCMD_PULL = "pull"
    SUBCMD_PUSH = "push"
    SUBCMD_BACKUP = "backup"
    SUBCMD_RESTORE = "restore"

    # git commands
    GIT_CMD_REMOTE = "remote"
    GIT_CMD_PUSH = "push"
    GIT_CMD_PULL = "pull"
    GIT_CMD_CLONE = "clone"
    GIT_CMD_REMOTE = "remote"
    GIT_CMD_STATUS = "status"
    GIT_CMD_BRANCH = "branch"
    GIT_CMD_REV_PARSE = "rev-parse"
    GIT_CMD_FETCH = "fetch"

    # Ignore node_modules which use to have a huge directory structure
    FILTER_NODE_MODULES = "node_modules"
    # Ignore .venv which use to have a huge directory structure
    FILTER_VENV = ".venv"
    # List for the directories to filter to accelerate the .git traverse.
    FILTERS = (FILTER_NODE_MODULES, FILTER_VENV)

    SUBP_CAPTURE_OUTPUT = "capture_output"

    CHECK_MODIFIED = "modified"
    CHECK_ADDED = "added"
    CHECK_UNKNOWN = "unknown"
    CHECK_NO_TRACKED = "no-tracked"
    CHECK_DELETED = "deleted"
    CHECK_NO_REMOTES = "no-remotes"
    CHECK_MISS_REMOTE = "miss-remote-branch"
    CHECK_REMOTE_SYNC = "not-synced"

    ERR_NOT_IMPLEMENTED = "Not Implemented"


def git(*args, **kargs):
    """Wrapper to invoke git commands"""
    if _.KEY_CWD not in kargs:
        raise KeyError(f"'{_.KEY_CWD}'")
    if _.SUBP_CAPTURE_OUTPUT not in kargs:
        kargs[_.SUBP_CAPTURE_OUTPUT] = True
    _cmd = [_.GIT, *args]
    result = subprocess.run(_cmd, **kargs, check=True)
    return result


def git_tb_all(basedir, f, *args, **kargs):
    """Traverse file system to find git repositories starting at the specific
    directory, and for each repository detected, run the function with the
    passing the arguments. It does not find submodules, it stop depth searching
    when the first repository is found.

    :param basedir: This is the path where start to traverse the file system.
    :param f: It is the reference to the function to call when a git repository
    is detected.
    :param *args: It is the positional arguments when invoking f.
    :param **kargs: It is the no positional arguments when invoking f.
    """
    for item in os.walk(basedir, topdown=True):
        if _.HIDDEN_GIT in item[_.WALK_DIRNAMES]:
            kargs[_.KEY_CWD] = basedir
            f(*args, **kargs)
        else:
            # Prune some well known directories
            for filter_item in _.FILTERS:
                if filter_item in item[_.WALK_DIRNAMES]:
                    item[_.WALK_DIRNAMES].remove(filter_item)
            # Recursive call to the remaining directories
            for new_dir in item[_.WALK_DIRNAMES]:
                git_tb_all(os.path.join(basedir, new_dir), f, *args, **kargs)
        break


# pylint: disable=W0613
def git_tb_list_helper(*args, **kargs):
    """Helper function to print the name of the repository when traversing
    the file system.

    :param *args: The positional arguments. Not used.
    :param **kargs: The no positional arguments. Not used.
    """
    print(f"{kargs[_.KEY_CWD]}")


def git_tb_list():
    """It represent the 'list' subcommand to traverse and print the path for
    the git repositories found."""
    git_tb_all(WORKSPACE, git_tb_list_helper)


def git_tb_check_print(summary: dict):
    """Print summary of indicators of interest detected for a git repository.

    :param summary: dictionary filled with _.CHECK_* keys when the condition
    was detected for the git repository.
    """
    str_add_files = "added files: {}"
    str_mod_files = "modified files: {}"
    str_del_files = "deleted files: {}"
    str_no_track_files = "no tracked files: {}"
    str_unknown_files = "unknown: {}"
    str_no_remotes = "has no remotes: {}"
    str_miss_remote = "no remote branch for: {}"
    str_remote_sync = "branches not sync on remote: {}"

    str_unexpected_key_value = "unexpected key {} with value {}"

    for key, value in summary.items():
        if key == _.CHECK_ADDED:
            print(str_add_files.format(value))
        elif key == _.CHECK_MODIFIED:
            print(str_mod_files.format(value))
        elif key == _.CHECK_DELETED:
            print(str_del_files.format(value))
        elif key == _.CHECK_NO_TRACKED:
            print(str_no_track_files.format(value))
        elif key == _.CHECK_UNKNOWN:
            print(str_unknown_files.format(value))
        elif key == _.CHECK_NO_REMOTES:
            if value:
                print(str_no_remotes.format(value))
        elif key == _.CHECK_MISS_REMOTE:
            print(str_miss_remote.format(value))
        elif key == _.CHECK_REMOTE_SYNC:
            print(str_remote_sync.format(value))
        else:
            logging.warning(str_unexpected_key_value, key, value)


def git_tb_check_proc_general(summary: dict, cwd: str):
    """
    General checks based on 'git status --ignore-submodules --porcelain'

    :param summary: Dictionary where to update the different keys about the states.
    :param cwd: is the current working directory for the git repository to analyze.
    """
    result = git(
        _.GIT_CMD_STATUS,
        "--ignore-submodules",
        "--porcelain",
        cwd=cwd,
        capture_output=True,
    )
    output = result.stdout.decode(_.UTF_8)
    if output == "":
        return summary
    lines = output.split("\n")
    if len(lines) == 0:
        return summary
    for line in lines:
        if line == "":
            continue
        if line[0:2] == " M" or line[0:2] == "M ":
            summary[_.CHECK_MODIFIED] = summary.get(_.CHECK_MODIFIED, 0) + 1
        elif line[0:2] == "A ":
            summary[_.CHECK_ADDED] = summary.get(_.CHECK_ADDED, 0) + 1
        elif line[0:2] == "D " or line[0:2] == " D":
            summary[_.CHECK_DELETED] = summary.get(_.CHECK_DELETED, 0) + 1
        elif line[0:2] == "??":
            summary[_.CHECK_NO_TRACKED] = summary.get(_.CHECK_NO_TRACKED, 0) + 1
        else:
            summary[_.CHECK_UNKNOWN] = summary.get(_.CHECK_UNKNOWN, 0) + 1
    return summary


def git_read_local_branches(cwd: str) -> list:
    """Read the list of local branches and return as a list of strings.

    :param cwd: The path for the analyzed repository.

    :return: List of local branches."""
    try:
        result = git(
            _.GIT_CMD_BRANCH,
            "--omit-empty",
            "--no-color",
            "--format=%(refname:short)",
            cwd=cwd,
        ).stdout.decode(_.UTF_8)
        if not result:
            return []
        result = result.splitlines()
        result = [x for x in result if not x.startswith("heads/")]
        return result
    # pylint: disable=W0718
    except Exception as e:
        logging.error(e)
        return None


def git_read_remote_branches(cwd: str, remotes: list) -> list:
    """Read all the remote branches for all the remotes.

    :param cwd: The current work directory for the working repository.
    :param remotes: List of remote names.

    :return: A list kind of ('origin/1-feature', 'origin/2-fix-typo') and so on.
    """
    try:
        result = git(
            _.GIT_CMD_BRANCH,
            "--omit-empty",
            "--no-color",
            "--format=%(refname:short)",
            "--remotes",
            cwd=cwd,
        ).stdout.decode(_.UTF_8)
        if not result:
            return []
        result = result.splitlines()
        remotes = [list(x.keys())[0] for x in remotes]
        # We can receive something like:
        #
        # origin/2-make-generate-client
        # origin
        # origin/main
        # origin/update-license
        # origin/update-readme
        #
        # And we would need to remove the 'origin' entry.
        result = [x for x in result if x not in remotes]
        return result
    # pylint: disable=W0718
    except Exception as e:
        logging.error(e)
        return None


def git_tb_check_proc_remotes(summary: dict, cwd: str):
    """Verify if the repository has any remote, and if the remotes are on sync.

    :param summary: is set _.CHECK_NO_REMOTES when no remotes, and
    _.CHECK_NO_ON_SYNC_REMOTES when some local branch is not on sync with the
    tracked remote branch, or no remote branch associated.
    :param cwd: is the path to the git repo being analyzed.

    :return: the modified summary dictionary, just to allow concatenate some
    operation with the result.
    """
    remotes = git_read_remotes(cwd)
    if remotes is None or len(remotes) == 0:
        summary[_.CHECK_NO_REMOTES] = True

    # Detect if some local branch does not have remote, or if the local branch
    # is not on sync with the remote branch (should point the same commit)
    local_branches = git_read_local_branches(cwd)
    if not local_branches:
        return summary

    remote_branches = git_read_remote_branches(cwd, remotes)
    remote_branch = ""
    for branch in local_branches:
        was_found = False
        for remote in remotes:
            if list(remote.keys())[0] + "/" + branch in remote_branches:
                remote_branch = list(remote.keys())[0] + "/" + branch
                was_found = True
                break

        if not _ARGS.is_checking_remote:
            continue

        if not was_found:
            # This local branch has not homologous remote
            summary[_.CHECK_MISS_REMOTE] = summary.get(_.CHECK_MISS_REMOTE, [])
            summary[_.CHECK_MISS_REMOTE].append(branch)
            continue

        has_sync_commit = False
        for remote in remotes:
            if list(remote.keys())[0] + "/" + branch in remote_branches:
                remote_branch = list(remote.keys())[0] + "/" + branch
            local_hash = git(_.GIT_CMD_REV_PARSE, branch, cwd=cwd).stdout.decode(
                _.UTF_8
            )
            remote_hash = git(
                _.GIT_CMD_REV_PARSE, remote_branch, cwd=cwd
            ).stdout.decode(_.UTF_8)
            if local_hash == remote_hash:
                has_sync_commit = True
                break
        if not has_sync_commit:
            summary[_.CHECK_REMOTE_SYNC] = summary.get(_.CHECK_REMOTE_SYNC, [])
            summary[_.CHECK_REMOTE_SYNC].append(branch)
    return summary


def git_tb_check_helper(*args, **kargs):
    """Helper to check the current repository. This generates a summary
    dictionary with the detected indicators, and then print the results
    for the current repository."""
    _cwd = kargs[_.KEY_CWD]
    summary = {}

    # Analyze current repository
    git_tb_check_proc_general(summary, _cwd)
    git_tb_check_proc_remotes(summary, _cwd)

    # Print report for the current repository if exists any indicator
    if len(summary.keys()) > 0:
        logging.info('repository at: "%s"', kargs[_.KEY_CWD])
        git_tb_check_print(summary)


def git_tb_check():
    """Check subcommand by traversing the repositories and running
    git_tb_check_helper for every detected repository in the WORKSPACE."""
    git_tb_all(WORKSPACE, git_tb_check_helper, stdout=None)


def git_tb_pull_helper(*args, **kargs):
    """Helper for the pull operation so this one operate in the current
    repository.

    :param *args: positional arguments. Not used here.
    :param **kargs: no positional arguments. It is used the current working dir
    which represent where the repository is located in the file system."""
    logging.info('repository at: "%s"', kargs[_.KEY_CWD])
    git(_.GIT_CMD_PULL, *args, **kargs)


def git_tb_pull(*args, **kargs):
    """Pull remote repositories for all the traversed repositories. The
    arguments are propagated to the helper function."""
    git_tb_all(WORKSPACE, git_tb_pull_helper, *args, **kargs)


def get_priority_git_remotes():
    """Return the prioritary remote names read from GIT_REMOTES environment
    variable; each remote name is separated by ',' character. The order matter
    as the push operation make the operation with the first valid found."""
    remotes = os.environ.get(_.ENV_GIT_REMOTES, _.GIT_REMOTES_DEFAULT).split(",")
    return remotes


def git_tb_push_helper(*args, **kargs):
    """Helper to traverse repositories and push to the remotes to sync the
    current"""
    try:
        cwd = kargs[_.KEY_CWD]
        remotes = git_remote_list(cwd)
        for remote in get_priority_git_remotes():
            if remote in remotes:
                git(_.GIT_CMD_PUSH, remote, "--all", cwd=cwd)
                return
        logging.warning("%s: repository not pushed", cwd)
    # pylint: disable=W0718
    except Exception as e:
        logging.error("%s: %s", cwd, str(e))


def git_tb_push():
    """Push subcommand which traverse all the git repositories and try to push
    the changes to remotes for syncing the information.
    """
    git_tb_all(WORKSPACE, git_tb_push_helper)


def git_remote_list(path):
    """Get the name list of remote repositories for a given git repository
    located at path.

    :param path: The relative location of the git repository using WORKSPACE as
    the base repository."""
    return git(_.GIT_CMD_REMOTE, cwd=path).stdout.decode(_.UTF_8).splitlines()


def git_read_remotes(path: str) -> list:
    """Read remotes for a given repository located at path.

    :param path: A valid path to a git repository using as base directory the
    WORKSPACE value.

    :return: A list with a remote-name -> url key value pairs.
    """
    try:
        data = []
        for key in git_remote_list(path):
            url = (
                git(_.GIT_CMD_REMOTE, "get-url", key, cwd=path)
                .stdout.decode(_.UTF_8)
                .split()[0]
            )
            data.append({key: url})
        return data
    # pylint: disable=W0718
    except Exception as e:
        logging.warning(e)
        return []


def helper_path_to_name(path: str) -> str:
    """Translate a repository path in a valid name to use for the workspace.yaml
    file. In other words, replace ("/", " ") by the "-" character.

    :param path: A valid repository path.

    :return: The repository name."""
    return os.path.realpath(path).replace("/", "-").replace(" ", "-")


def git_tb_backup_helper(*args, **kargs):
    """Helper which allow to fill the context information for the current
    repository during the traverse of WORKSPACE.

    :param *args: positional arguments.
    :param **kargs: no positional arguments.
      - _.KEY_CONTEXT store the dictionary that represent the workspace.yaml
        file.
      - _.KEY_CWD is the current working directory for the actual repository.
    """
    context = kargs[_.KEY_CONTEXT]
    workspace_name = helper_path_to_name(os.path.realpath(WORKSPACE)) + "-"
    name = helper_path_to_name(os.path.realpath(kargs[_.KEY_CWD]))
    name = name.removeprefix(workspace_name)
    path = os.path.realpath(kargs[_.KEY_CWD])
    path = path.removeprefix(WORKSPACE + "/")
    remotes = git_read_remotes(path)
    if remotes is None or len(remotes) == 0:
        logging.warning("repository '%s' at: '%s' without remotes", name, path)
    repo = {"name": name, "path": path, "remotes": remotes}
    context["repositories"].append(repo)


def git_tb_backup():
    """Generate workspace.yml as a backup source. Keep in mind if some branch
    is not on sync with the remote ones, you could lost information if you
    remove some repository locally. Check with 'git tb check' before delete
    the repository.
    """
    current_data = {}
    _workspace_file = os.path.join(WORKSPACE, _.WORKSPACE_FILE)
    if os.path.exists(_workspace_file):
        with open(_workspace_file, "rt", encoding="UTF-8") as fi:
            current_data = yaml.safe_load(fi)
    data = {
        "base": WORKSPACE,
        "upstream-order": os.environ.get(
            _.ENV_GIT_REMOTES, _.GIT_REMOTES_DEFAULT
        ).split(","),
        "modified-at": datetime.now().isoformat(),
        "repositories": [],
    }
    git_tb_all(WORKSPACE, git_tb_backup_helper, context=data)
    data.update(current_data)
    with open(_workspace_file, "wt", encoding="UTF-8") as fo:
        fo.write("# file: " + _.WORKSPACE_FILE + "\n")
        fo.write("# generated by: git-tb backup\n")
        fo.write("---\n")
        yaml.safe_dump(data, fo)


def is_invalid_repo_path(path: str) -> bool:
    """Check when a path is an invalid repository path. It evaluates that it
    is not an absolute path (it is relative to WORKSPACE variable). If the path
    is None or an empty string. If the path try to go up directory, at the
    begin or in the middle.

    :param path: The string with the path to the repository.

    :return: True if the path is invalid, else False.
    """
    if not path:
        return True
    if path[0] == "/":
        return True
    if path[0:2] == "..":
        return True
    if "/../" in path:
        return True
    return False


def git_tb_restore_helper(name, path, repo):
    """Helper to restore a specific repository given the name, path and
    repository.

    :param name: Only used for printing.
    :param path: The path where to clone the repository.
    :param repo: The HTTPS or SSH git remote reference for the repository.
    """
    logging.info("restoring repo %s at %s", name, path)
    target_path = os.path.join(WORKSPACE, path)
    parent_target_path = os.path.dirname(target_path)
    if not os.path.exists(parent_target_path):
        os.mkdir(parent_target_path)

    for remote in repo["remotes"]:
        for key, value in remote.items():
            if not os.path.exists(target_path):
                git(
                    _.GIT_CMD_CLONE,
                    "--origin",
                    key,
                    value,
                    target_path,
                    cwd=parent_target_path,
                    check=True,
                )
            else:
                git(_.GIT_CMD_REMOTE, "add", key, value, cwd=target_path, check=False)
        git(_.GIT_CMD_FETCH, "--all", cwd=target_path, check=True)


def git_tb_restore():
    """Restore a workspace cloning repositories and fetching all the remote
    repositories."""
    _workspace_file = os.path.join(WORKSPACE, _.WORKSPACE_FILE)
    with open(_workspace_file, "rt", encoding="UTF-8") as fi:
        data = yaml.safe_load(fi)
    if "modified-at" in data:
        print(f"last modified on: {data['modified-at']}")
    os.environ[_.ENV_GIT_REMOTES] = ",".join(
        data.get("upstream-order", _.GIT_REMOTES_DEFAULT.split(","))
    )

    for repo in data["repositories"]:
        # Sanitize attributes
        name = repo.get("name", None)
        if not name:
            continue
        path = repo.get("path", None)
        if is_invalid_repo_path(path):
            logging.warning("ignoring repo: repo %s has invalid path %s", name, path)
            continue
        if not repo["remotes"]:
            logging.warning("ignoring repo: repo %s does not have remotes", name)
            continue

        try:
            git_tb_restore_helper(name, path, repo)
        # pylint: disable=W0718
        except Exception as e:
            logging.error(e)


def git_tb_args():
    """Configure argument parser and return it."""
    parser = argparse.ArgumentParser(prog=_.PROG, description="git toolbox")
    parser.add_argument(
        "-d",
        "--debug",
        help="Enable debug log level",
        action="store_true",
        dest="is_log_debug",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable trace log level",
        action="store_true",
        dest="is_log_verbose",
        default=False,
    )
    parser.add_argument(
        "-V",
        "--version",
        help="Show the tool version",
        action="store_true",
        dest="version",
        default="v1.0.0",
    )
    subparsers = parser.add_subparsers(dest="command")

    # pylint: disable=W0612
    print_parser = subparsers.add_parser(
        _.SUBCMD_LIST, help="List the repositories detected in the workspace"
    )
    check_parser = subparsers.add_parser(
        _.SUBCMD_CHECK, help="Check repositories for pending local changes"
    )
    check_parser.add_argument(
        "--no-remote",
        help="Do not check remote sync",
        action="store_false",
        dest="is_checking_remote",
        default=True,
    )

    # pylint: disable=W0612
    pull_parser = subparsers.add_parser(
        _.SUBCMD_PULL, help="Run pull for all the repositories in the workspace"
    )
    # pylint: disable=W0612
    push_parser = subparsers.add_parser(
        _.SUBCMD_PUSH,
        help="Run push for all the repositories for upstream, or origin (the first found)",
    )
    # pylint: disable=W0612
    backup_parser = subparsers.add_parser(
        _.SUBCMD_BACKUP,
        help="Generate a '"
        + _.WORKSPACE_FILE
        + "' file that can be used to recover the workspace state",
    )
    # pylint: disable=W0612
    restore_parser = subparsers.add_parser(
        _.SUBCMD_RESTORE,
        help="Restore from a '" + _.WORKSPACE_FILE + "' file all the repositories",
    )

    return parser


def setup_logs(args):
    """Setup the logs and DEBUG level if it was specified by parameters."""
    logging.basicConfig(level=logging.INFO)
    if args.is_log_debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("setting DEBUG log level")


def get_subcommands_map():
    """Return the composed map between subcommand and the entry point function.

    :return: A dictionary {"subcommand" -> function}.
    """
    return {
        _.SUBCMD_LIST: git_tb_list,
        _.SUBCMD_CHECK: git_tb_check,
        _.SUBCMD_PULL: git_tb_pull,
        _.SUBCMD_PUSH: git_tb_push,
        _.SUBCMD_BACKUP: git_tb_backup,
        _.SUBCMD_RESTORE: git_tb_restore,
    }


def main():
    """Entry point for git toolbox."""
    # pylint: disable=W0603
    global _ARGS
    subcommands = get_subcommands_map()
    _ARGS = git_tb_args().parse_args()
    setup_logs(_ARGS)
    subcommand = _ARGS.command
    if not subcommand in subcommands:
        print("""git toolbox: helper to keep your git repositories in good shape\n""")
        git_tb_args().print_help()
        return 1
    return subcommands[subcommand]()


if __name__ == "__main__":
    sys.exit(main())
