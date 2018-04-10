import time


class Light(object):
    def __init__(self):
        self.is_open = False

    def get_light_status(self):
        return self.is_open

    def open_light(self):
        if self.is_open:
            return self.is_open
        else:
            # open door

            time.sleep(3)

    def close_light(self):
        self.is_open = False
        return self.is_open


