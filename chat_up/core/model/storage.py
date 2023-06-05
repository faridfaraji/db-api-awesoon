import abc


class Storage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def store_stuff(self, stuff):
        pass

    @abc.abstractmethod
    def get_stuff(self):
        pass
