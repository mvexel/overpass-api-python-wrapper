import overpass


class TestSlots:
    def setup(self):
        self.api = overpass.API(debug=True)

    def test_slots_available(self):
        assert 0 <= self.api.slots_available <= 2

    def test_slots_running(self):
        assert isinstance(self.api.slots_running, tuple)

    def test_slots_waiting(self):
        assert isinstance(self.api.slots_waiting, tuple)
