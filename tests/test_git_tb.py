#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

# Unit tests for git-tb tool
from unittest.mock import Mock, patch
from git_tb import *


def test_git_raise_key_error():
    try:
        git()
    except KeyError as e1:
        assert str(e1) == "'{}'".format(_.KEY_CWD)


def test_git_default_capture_output():
    # Define el comportamiento deseado del mock del subproceso
    mock_subprocess_run = Mock()
    mock_subprocess_run.return_value.returncode = 0

    # Crea el mock de subprocess.run y lo aplica en un bloque with
    with patch("subprocess.run", mock_subprocess_run):
        # Llama a la función 'git'
        result = git("version", cwd=".")

        # Verifica que el comportamiento esperado se haya invocado
        mock_subprocess_run.assert_called_once_with(
            ["git", "version"], capture_output=True, cwd="."
        )
        mock_subprocess_run.assert_called_once_with(["version"], cwd=".")

        # Verifica que la función devuelva el resultado esperado
        assert result.returncode == 0


def test_git_raise_key_error():
    # Define el comportamiento deseado del mock del subproceso
    mock_subprocess_run = Mock()
    mock_subprocess_run.return_value.returncode = 0

    # Crea el mock de subprocess.run y lo aplica en un bloque with
    with patch("subprocess.run", mock_subprocess_run):
        result = git("version", cwd=".", capture_output=True)
        mock_subprocess_run.assert_called_once_with(
            ["git", "version"], capture_output=True, cwd="."
        )
        assert result.returncode == 0


def test_git_capture_output_false():
    # Define el comportamiento deseado del mock del subproceso
    mock_subprocess_run = Mock()
    mock_subprocess_run.return_value.returncode = 0

    # Crea el mock de subprocess.run y lo aplica en un bloque with
    with patch("subprocess.run", mock_subprocess_run):
        result = git("status", cwd=".", capture_output=False)
        mock_subprocess_run.assert_called_once_with(
            ["git", "status"], capture_output=False, cwd="."
        )
        assert result.returncode == 0


# -----------------------------------------------------------------------


def test_git_tb_all():
    pass


def test_git_tb_list_helper():
    git_tb_list_helper(*args, **kargs)
