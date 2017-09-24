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

    def remove_Element(self, object):
        with open(self.file, 'r', encoding="utf8") as f:
            data = json.load(f)

        with open(self.file, 'w', encoding="utf8") as f:
            del data[object]
            json.dump(data, f, indent=" ", ensure_ascii=False)

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

    def get_dict(self):
        with open(self.file, 'r') as f:
            return json.load(f)


channel = Element("C:\\Users\\Linus\\PycharmProjects\\Support-Manager\\channels.json")  # TODO: adjust paths
prefix = Element("C:\\Users\\Linus\\PycharmProjects\\Support-Manager\\prefixes.json")
ticket = Element("C:\\Users\\Linus\\PycharmProjects\\Support-Manager\\tickets.json")
