from termcolor import cprint

from handlers import database


class LiveConfig:
    """
    To add a new value to the live config system, make sure it has a default value in this class's __init__ method,
    and is declared in this class's __slots__ right below.

    Note: You need to call live_config.set() in order to keep it synced with the db. See that method for more details
    but make sure not to set values directly without them being synced in the db!!
    """

    __slots__ = ('dailydive_operator',)

    def __init__(self):
        pass
        self.dailydive_operator = 372599532975816715

    def load(self):
        for name in self.__slots__:
            default = getattr(self, name)
            value = database.get_config_value(name, default)
            if isinstance(value, type(default)):
                setattr(self, name, value)
            else:
                self.set(name, value)
        cprint("Successfully loaded all live config values!", "green")

    def set(self, name, value=None):
        """
        This is kinda intended as a wrapper for the associated db method. It does the same thing but also makes sure it's synced locally.
        :param name: The name of the attribute we're setting. It's important that the name matches a value in lc.__slots__.
        :param value: The value we want to set it to. If it's left empty, it will just be synced in the db to its
                      current local value. Do this if you need to perform some operation directly on the local attribute first.
        """
        if name not in self.__slots__:
            return
        if value is not None:
            setattr(self, name, value)
        database.set_config_value(name, getattr(self, name))


lc = LiveConfig()
