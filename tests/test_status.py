import datetime

import overpass


RESPONSE_TEXT = b'''Connected as: 3268165505
Current time: 2021-09-03T14:40:17Z
Rate limit: 2
1 slots available now.
Slot available after: 2021-09-03T14:41:37Z, in 80 seconds.
Currently running queries (pid, space limit, time limit, start time):
'''


class TestSlots:
    def setup(self):
        self.api = overpass.API(debug=True)
        self.requests = None

    def teardown(self):
        assert self.requests.get.called
        assert self.requests.get.call_args.args == ('https://overpass-api.de/api/status',)
        assert not self.requests.post.called

    def test_slots_available(self, requests):
        requests.response._content = RESPONSE_TEXT
        self.requests = requests

        assert 0 <= self.api.slots_available <= 2

    def test_slots_running(self, requests):
        requests.response._content = RESPONSE_TEXT
        self.requests = requests

        assert isinstance(self.api.slots_running, tuple)

    def test_slots_waiting(self, requests):
        requests.response._content = RESPONSE_TEXT
        self.requests = requests

        assert self.api.slots_waiting == (datetime.datetime(2021, 9, 3, 14, 41, 37, tzinfo=datetime.timezone.utc),)
