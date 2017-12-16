import os

def data_path(name):
    """
    Return the absolute path to a file in the simVCF/test/data directory.
    The name specified should be relative to simVCF/test/data.
    """
    return os.path.join(os.path.dirname(__file__), "data", name)
