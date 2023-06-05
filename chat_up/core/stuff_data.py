from cookiecutter.core.memory import Memory
import re


class StuffData:
    @staticmethod
    def populate_stuff_data(data_adaptor, datastore: Memory):
        for stuff in data_adaptor.get_stuff():
            # Buisness logic: keep only the names starting with capital
            if re.findall('[A-Z]+[a-z]+$', stuff.name):
                datastore.store_stuff(stuff)
