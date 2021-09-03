import pytest
import mock

import overpass


@pytest.fixture(scope='function')
def requests(monkeypatch):
    mocker = mock.MagicMock()
    mocker.response = overpass.api.requests.Response()

    mocker.response.status_code = 200

    mocker.get.return_value = mocker.response
    mocker.post.return_value = mocker.response

    monkeypatch.setattr(overpass.api, 'requests', mocker)

    yield mocker
