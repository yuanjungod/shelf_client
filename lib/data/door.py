
class Door(object):
    def __init__(self):
        self.is_open = False

    def get_door_status(self):
        for i in range(5):
            yield True
        yield False
