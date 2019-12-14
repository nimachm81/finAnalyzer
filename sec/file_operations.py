"""
Read or write financial data to folder.

"""

__all__ = ["SECFileOp"]


import os


class SECFileOp:
    def __init__(self, data_folder):
        """Read or write SEC data to folder.

        parameters
        --------
        data_folder: str
            data will be read from or write to this folder
        """
        self.data_folder = data_folder
        assert os.path.exists(data_folder)

