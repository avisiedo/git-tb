#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

# Unit tests for git-tb tool
from unittest.mock import Mock, patch, MagicMock

from git_tb.git_tb import *
from git_tb.git_tb import _

from types import SimpleNamespace
from unittest.mock import patch

import git_tb.git_tb as gt

from types import SimpleNamespace

from git_tb.git_tb import (
    helper_path_to_name,
    is_invalid_repo_path,
    get_priority_git_remotes,
    git_remote_list,
    git_read_remotes,
    _,
)

import os


def test_git_raise_key_error_on_cwd_absence():
    try:
        git()
    except KeyError as e1:
        assert str(e1) == "'{}'".format(_.KEY_CWD)


def test_git_defaults():
    # Define the wished behavior for subprocess mock
    mock_subprocess_run = Mock()
    mock_subprocess_run.return_value.returncode = 0

    # Create subprocess.run mock and use it
    with patch("subprocess.run", mock_subprocess_run):
        # Call SUT by invoking git wrapper with 'version' subcommand
        result = git("version", cwd=".")

        # Verify that the expected behavior was invoked
        mock_subprocess_run.assert_called_once_with(
            ["git", "version"], cwd=".", capture_output=True, check=True
        )

        # Verify the function returned the expected behavior
        assert result.returncode == 0


def test_git_version_success():
    mock_subprocess_run = Mock()
    mock_subprocess_run.return_value.returncode = 0

    with patch("subprocess.run", mock_subprocess_run):
        result = git("version", cwd=".", capture_output=True)
        mock_subprocess_run.assert_called_once_with(
            ["git", "version"], capture_output=True, cwd=".", check=True
        )
        assert result.returncode == 0


def test_git_capture_output_false():
    mock_subprocess_run = Mock()
    mock_subprocess_run.return_value.returncode = 0

    with patch("subprocess.run", mock_subprocess_run):
        result = git("status", cwd=".", capture_output=False)
        mock_subprocess_run.assert_called_once_with(
            ["git", "status"], capture_output=False, cwd=".", check=True
        )
        assert result.returncode == 0


# -----------------------------------------------------------------------


def test_git_tb_all():
    mock_os_walk = MagicMock()
    index_os_walk = 0

    def side_effect_os_walk(*args, **kwargs):
        global index_os_walk
        ordered_args = (
            (["/base"], {"topdown": True}, )   
        )
        ordered_responses = (
            ("/base", [_.HIDDEN_GIT], []),
        )

        if *args == *ordered_args[index_os_walk] and **kwargs == **ordered_args[index_os_walk]:
            index_os_walk = index_os_walk + 1
            return ordered_responses[index_os_walk]
        else:
            index_os_walk = index_os_walk + 1
            raise AssertionError(f"Unexpected os.walk call: [{args}], \{{kargs}\}")

    mock_os_walk.side_effect = side_effect_os_walk
    mock_os_walk.call_args("/base", topdown=True).return_value. = [("/base", [_.HIDDEN_GIT], [])]
    with patch("os.walk", mock_os_walk):
        helper = Mock()
        git_tb_all("/base", helper)
        mock_os_walk.assert_called_once_with("/base", topdown=True)
        helper.assert_called_once_with(cwd="/base")


# -----------------------------------------------------------------------


def test_git_tb_list_helper():
    args = []
    kargs = {_.KEY_CWD: "."}
    git_tb_list_helper(*args, **kargs)

def test_helper_path_to_name(tmp_path):
    repo = tmp_path / "my repo"
    repo.mkdir()
    name = helper_path_to_name(str(repo))
    assert "/" not in name
    assert " " not in name
    assert "-" in name


def test_is_invalid_repo_path():
    assert is_invalid_repo_path(None) is True
    assert is_invalid_repo_path("") is True
    assert is_invalid_repo_path("/absolute/path") is True
    assert is_invalid_repo_path("..") is True
    assert is_invalid_repo_path("foo/../bar") is True
    assert is_invalid_repo_path("relative/path") is False


def test_get_priority_git_remotes_default_and_env(monkeypatch):
    # default
    monkeypatch.delenv(_.ENV_GIT_REMOTES, raising=False)
    defaults = get_priority_git_remotes()
    assert isinstance(defaults, list)
    assert defaults == _.GIT_REMOTES_DEFAULT.split(",")

    # custom env
    monkeypatch.setenv(_.ENV_GIT_REMOTES, "upstream,origin,custom")
    custom = get_priority_git_remotes()
    assert custom == ["upstream", "origin", "custom"]


def test_git_remote_list_and_git_read_remotes():
    # Patch the internal git wrapper to avoid real subprocess calls
    def fake_git(*args, **kargs):
        # emulate `git remote`
        if args and args[0] == _.GIT_CMD_REMOTE and len(args) == 1:
            return SimpleNamespace(stdout=b"origin\nupstream\n")
        # emulate `git remote get-url <name>`
        if args and args[0] == _.GIT_CMD_REMOTE and args[1] == "get-url":
            key = args[2]
            return SimpleNamespace(stdout=(f"{key}@example.com:repo.git\n").encode("utf-8"))
        raise AssertionError(f"Unexpected git call: {args}")

    with patch("git_tb.git_tb.git", side_effect=fake_git):
        remotes = git_remote_list("some/path")
        assert remotes == ["origin", "upstream"]

        data = git_read_remotes("some/path")
        assert isinstance(data, list)
        merged = {k: v for d in data for k, v in d.items()}
        assert "origin" in merged
        assert merged["origin"] == "origin@example.com:repo.git"


def test_git_tb_check_proc_general_counts():
    summary = {}

    def fake_git(*args, **kargs):
        if args and args[0] == gt._.GIT_CMD_STATUS:
            out = b" M file1\nA file2\nD file3\n?? file4\nUU file5\n"
            return SimpleNamespace(stdout=out)
        raise AssertionError("Unexpected git call")

    with patch("git_tb.git_tb.git", side_effect=fake_git):
        res = gt.git_tb_check_proc_general(summary, cwd=".")
        assert res[gt._.CHECK_MODIFIED] == 1
        assert res[gt._.CHECK_ADDED] == 1
        assert res[gt._.CHECK_DELETED] == 1
        assert res[gt._.CHECK_NO_TRACKED] == 1
        assert res[gt._.CHECK_UNKNOWN] == 1


def test_git_read_local_branches_and_remote_branches():
    def fake_git_local(*args, **kargs):
        if args and args[0] == gt._.GIT_CMD_BRANCH and "--remotes" not in args:
            return SimpleNamespace(stdout=b"main\nfeature\nheads/old\n")
        if args and args[0] == gt._.GIT_CMD_BRANCH and "--remotes" in args:
            return SimpleNamespace(stdout=b"origin/feature\norigin\norigin/main\n")
        raise AssertionError("Unexpected git call")

    with patch("git_tb.git_tb.git", side_effect=fake_git_local):
        locals_ = gt.git_read_local_branches(".")
        assert "main" in locals_
        assert all(not x.startswith("heads/") for x in locals_)

        remotes_lines = gt.git_read_remote_branches(".", remotes=[{"origin": "u"}])
        assert "origin/main" in remotes_lines
        assert "origin" not in remotes_lines


def test_git_tb_backup_helper(tmp_path, monkeypatch):
    # Set WORKSPACE to tmp_path
    monkeypatch.setattr(gt, "WORKSPACE", str(tmp_path))

    # Create repo dir
    repo_dir = tmp_path / "repo1"
    repo_dir.mkdir()

    # Case with remotes
    monkeypatch.setattr(gt, "git_read_remotes", lambda path: [{"origin": "u"}])
    ctx = {"repositories": []}
    gt.git_tb_backup_helper(context=ctx, cwd=str(repo_dir))
    assert len(ctx["repositories"]) == 1
    repo = ctx["repositories"][0]
    assert repo["name"].endswith("repo1")
    assert repo["path"] == "repo1"

    # Case without remotes logs a warning but still appends
    monkeypatch.setattr(gt, "git_read_remotes", lambda path: [])
    ctx2 = {"repositories": []}
    gt.git_tb_backup_helper(context=ctx2, cwd=str(repo_dir))
    assert len(ctx2["repositories"]) == 1


def test_git_tb_restore_helper_creates_and_calls_git(tmp_path, monkeypatch):
    # prepare workspace
    monkeypatch.setattr(gt, "WORKSPACE", str(tmp_path))

    # target repo path under workspace
    repo_path = "a/b/repo"
    name = "repo"

    calls = []

    def fake_git(*args, **kargs):
        calls.append((args, kargs))
        # emulate clone side-effect: create the target directory
        if args and args[0] == gt._.GIT_CMD_CLONE:
            target = args[-1]
            os.makedirs(target, exist_ok=True)
            return SimpleNamespace(stdout=b"")
        return SimpleNamespace(stdout=b"")

    repo = {"remotes": [{"origin": "git@example.com:r.git"}, {"upstream": "git@example.com:u.git"}]}

    with patch("git_tb.git_tb.git", side_effect=fake_git):
        gt.git_tb_restore_helper(name, repo_path, repo)

    # Expect at least one clone call and a fetch call
    assert any(call[0][0] == gt._.GIT_CMD_CLONE for call in calls)
    assert any(call[0][0] == gt._.GIT_CMD_FETCH for call in calls)
