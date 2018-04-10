import time


class Door(object):
    def __init__(self):
        self.is_open = False

    def get_door_status(self):
        for i in range(5):
            yield True
        yield False

    def open_door(self):
        if self.is_open:
            return True
        else:
            time.sleep(5)
            return False

    def close_door(self):
        if self.is_open:
            time.sleep(5)
            return True
        else:
            return False
