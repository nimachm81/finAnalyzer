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

    def _company_base_folder_exists(self, symbol):
        """Checks whether the company's base folder exists.

        parameters
        --------
        symbol: str
            The stock symbol, for example "aapl" for Apple Inc.

        returns
        --------
        :bool
            True: if base folder exists, False: otherwise
        """
        dir_path = os.path.join(self.data_folder, symbol)
        return os.path.exists(dir_path)

    def _create_company_base_folder(self, symbol):
        """Creates the company's base folder if it does not already exist.

        parameters
        --------
        symbol: str
            The stock symbol, for example "aapl" for Apple Inc.
        """
        if not self._company_base_folder_exists(symbol):
            dir_path = os.path.join(self.data_folder, symbol)
            os.mkdir(dir_path)

