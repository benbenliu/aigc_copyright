import os


def is_prod_environment():
    return os.environ['RUNTIME_ENV'] == 'prod'
