import json

class Element:
    def __init__(self, file):
        self.file = file

    def get(self, object):
        #try:
        with open(self.file, 'r') as f:
            data = json.load(f)
            value = data[object]

            try:
                return int(value)
            except:
                return value
        #except KeyError:
         #   raise IndexError

    def set(self, object, value):
        with open(self.file, 'r') as f:
            data = json.load(f)

        with open(self.file, 'w') as f:
            data[object] = value
            json.dump(data, f, indent=" ")

    def add_Element(self, object, value):
        self.set(object, value)

    def add_to_Value(self, object, value):
        current = self.get(object)
        self.set(object, current + value)

    def remove_from_Value(self, object, value):
        current = self.get(object)
        self.set(object, current - value)

    def rank_list(self):
        with open(self.file, 'r') as f:
            data = json.load(f)

        leaderboard = []

        for i in data:
            id = i
            value = data[i]
            leaderboard.append((id, value))
        leaderboard.sort(key=lambda element: element[1], reverse=True)

        return leaderboard

    def rank_position(self, id):
        leaderboard = self.rank_list()

        position = 0
        for i in leaderboard:
            position += 1
            if i[0] == id:
                break

        return position


channel = Element("C:\\Users\\Linus\\PycharmProjects\\Support-Manager\\channels.json")
prefix = Element("C:\\Users\\Linus\\PycharmProjects\\Support-Manager\\prefixes.json")
