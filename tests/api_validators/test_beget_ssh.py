from unittest.mock import patch
from tools.api_validators import beget_ssh


def test_missing(clean_env):
    r = beget_ssh.validate()
    assert not r.is_valid


def test_valid(clean_env):
    clean_env.setenv("BEGET_USER", "u")
    clean_env.setenv("BEGET_HOST", "srv.beget.ru")
    with patch("subprocess.run") as mock:
        mock.return_value.returncode = 0
        mock.return_value.stdout = "ok\n"
        r = beget_ssh.validate()
        assert r.is_valid


def test_invalid(clean_env):
    clean_env.setenv("BEGET_USER", "u")
    clean_env.setenv("BEGET_HOST", "srv.beget.ru")
    with patch("subprocess.run") as mock:
        mock.return_value.returncode = 255
        mock.return_value.stderr = "Permission denied"
        r = beget_ssh.validate()
        assert not r.is_valid
