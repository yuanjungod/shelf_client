import time


class Door(object):
    def __init__(self):
        self.is_open = False

    def get_door_status(self):
        for i in range(3):
            self.is_open = False
            yield True
        self.is_open = True
        yield False

    def open_door(self):
        self.is_open = True

    def close_door(self):
        if self.is_open:
            time.sleep(5)
            return True
        else:
            return False
