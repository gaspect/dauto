import unittest
from dauto.utils import Event, EventBuss


class Events(unittest.TestCase):
    eb = EventBuss()

    def test_events_topic_matching(self):
        @self.eb.subscribe(r'test.*')
        def event_handler(_):
            raise Exception()

        with self.assertRaises(Exception):
            self.eb.dispatch(Event("test.data", {}))


if __name__ == '__main__':
    unittest.main()
