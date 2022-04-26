
class Transaction:

    def __init__(self):
        self._list = list()

    def get_attributes(self):
        return self._list

    def add_attribute(self, attribute):
        self._list.append(attribute)

    def clear_attributes(self):
        self._list.clear()
