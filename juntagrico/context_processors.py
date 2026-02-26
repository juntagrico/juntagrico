import collections

from juntagrico.config import Config


class Vocabulary(collections.UserDict):
    def __getitem__(self, name):
        if name not in self.data:
            self.data[name] = Config.vocabulary(name)
        return self.data[name]


def vocabulary(request):
    return {"vocabulary": Vocabulary()}
