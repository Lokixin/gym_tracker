import pendulum
import pytest


@pytest.fixture
def mock_pendulum_now(mocker):
    mocked_now = pendulum.parse("2024-05-23T21:24:11.765570+02:00")
    mocker.patch("pendulum.now", return_value=mocked_now)
    return mocked_now
