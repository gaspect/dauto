import unittest
from dauto.utils import Event, EventBus
import queue


class Events(unittest.TestCase):
    eb = EventBus()
    q = queue.Queue()

    def test_events_topic_matching(self):
        @self.eb.subscribe(r'test.*')
        def event_handler(_):
            self.q.put(True)

        self.eb.dispatch(Event("test.data", {}))
        assert self.q.get(timeout=5)


if __name__ == '__main__':
    unittest.main()
