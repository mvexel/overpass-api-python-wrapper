import sys


class Python:
    version = (sys.version_info.major, sys.version_info.minor)

    @classmethod
    def less_3_7(cls):
        return cls.version < (3, 7)
