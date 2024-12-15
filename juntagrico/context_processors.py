import collections

from juntagrico.config import Config


def vocabulary(request):
    class Vocabulary(collections.UserDict):
        def __getitem__(self, name):
            if name not in self.data:
                self.data[name] = Config.vocabulary(name)
            return self.data[name]
    return {"vocabulary": Vocabulary()}
