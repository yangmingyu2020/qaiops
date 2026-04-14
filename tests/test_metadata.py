"""Tests for metadata extraction."""

from unittest.mock import patch

from qaiops.wrapper.metadata import get_cwd, get_project_id, get_timestamp


def test_get_cwd():
    cwd = get_cwd()
    assert isinstance(cwd, str)
    assert len(cwd) > 0


def test_get_timestamp():
    ts = get_timestamp()
    assert isinstance(ts, str)
    assert "T" in ts  # ISO 8601 format


def test_get_project_id_no_git():
    with patch("qaiops.wrapper.metadata.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()
        result = get_project_id()
        assert result is None


def test_get_project_id_in_git_repo():
    with patch("qaiops.wrapper.metadata.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "/home/user/projects/my-saas-app\n"
        result = get_project_id()
        assert result == "my-saas-app"
