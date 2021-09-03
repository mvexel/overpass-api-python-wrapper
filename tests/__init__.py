import os

RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(os.path.relpath(__file__))), 'resources')


def save_resource(file_name, data):
    with open(os.path.join(RESOURCE_PATH, file_name), 'wb') as f:
        f.write(data)


def load_resource(file_name):
    with open(os.path.join(RESOURCE_PATH, file_name), 'rb') as f:
        result = f.read()
    return result
