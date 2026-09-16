
from demo_repo.src.login import login


def test_login_button():
    assert login("alice", "password") is True
    assert login("", "") is False