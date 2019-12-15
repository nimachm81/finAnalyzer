"""
Read or write financial data to folder.

"""

__all__ = ["SECFileOp"]


import os

FILE_NAME_SEPARATOR = "_"
RAW_EXT = ".txt"
RAW_FOLDER_NAME = "raw"
COMPANY_INFO = "company_info"
FORM_10Q_TAG = "10-Q"
VERSION = 1.0


class SECFileOp:
    def __init__(self, data_folder):
        """Read or write SEC data to folder.

        parameters
        --------
        data_folder: str
            data will be read from or write to this folder
        """
        self.base_data_folder = data_folder
        assert os.path.exists(data_folder)
        self.current_company_folder = None

    @staticmethod
    def get_version_tag(self):
        """Get the file tag for this version. Every raw file will start with this tag.

        returns
        --------
        :str
            version tag
        """
        version_tag = "Version {}\n".format(VERSION)
        return version_tag

    def _create_raw_file_and_set_version_tag(self, file_name):
        """Create a file with the specified file name and write the version tag at the
        beginning of the file.

        parameters
        --------
        file_name: str
            file name, including its path and its extension

        returns
        --------
        :file
            opened file with tag
        """
        file = open(file_name, "w")
        file.write(self.get_version_tag())
        return file

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
        dir_path = os.path.join(self.base_data_folder, symbol)
        return os.path.exists(dir_path)

    def _create_company_base_folder_if_not_exists(self, symbol):
        """Creates the company's base folder if it does not already exist.

        parameters
        --------
        symbol: str
            The stock symbol, for example "aapl" for Apple Inc.
        """
        if not self._company_base_folder_exists(symbol):
            dir_path = os.path.join(self.base_data_folder, symbol)
            os.mkdir(dir_path)

    def _set_curren_companny_folder(self, symbol):
        """Moves to the company folder. The following the read/writes will be in this folder.

        parameters
        --------
        symbol: str
            The stock symbol, for example "aapl" for Apple Inc.
        """
        # check if folder exists and create otherwise
        self._create_company_base_folder_if_not_exists(symbol)

        # set as current folder
        self.current_company_folder = os.path.join(self.base_data_folder, symbol)
        # create default subfolders
        self._create_default_subfolders()

    def _create_default_subfolders(self):
        """Creates default sub-folders inside the current company folder, if they do not exist already."""
        assert self.current_company_folder is not None

        # raw folder for raw (unprocessed) data
        raw_folder = os.path.join(self.current_company_folder, RAW_FOLDER_NAME)
        if not os.path.exists(raw_folder):
            os.mkdir(raw_folder)

    def _write_raw_company_info(self, company_info):
        """Write raw company info to the current folder

        parameters
        --------
        company_info: str
            raw company info
        """
        file_name = COMPANY_INFO + RAW_EXT
        file_path = os.path.join(self.current_company_folder, RAW_FOLDER_NAME, file_name)
        file = self._create_raw_file_and_set_version_tag(file_path)
        file.write(company_info)
        file.close()

    def _write_raw_financial_statements(self, date, form_tag, financial_statements):
        """write raw financial statements to current folder

        parameters
        --------
        date: datetime.date
            date of the statements
        form_tag: str
            financial form tag for example 10-Q
        financial_statements: str
            raw financial statements
        """
        file_name = date.isoformat() + FILE_NAME_SEPARATOR + form_tag + RAW_EXT
        file_path = os.path.join(self.current_company_folder, RAW_FOLDER_NAME, file_name)
        file = self._create_raw_file_and_set_version_tag(file_path)
        file.write(financial_statements)
        file.close()

    def write_raw_company_info(self, symbol, company_info):
        """Write raw company info.

        parameters
        --------
        symbol: str
            stock symbol
        company_info: str
            raw financial statements
        """
        self._set_curren_companny_folder(symbol)
        self._write_raw_company_info(company_info)

    def write_raw_quarterly_10Q_financial_statements(self, symbol, date, financial_statements):
        """Write raw quarterly financial statements (10-Q forms).

        parameters
        --------
        symbol: str
            stock symbol
        date: datetime.date
            financial form release date
        financial_statements: str
            raw financial statements
        """
        self._set_curren_companny_folder(symbol)
        self._write_raw_financial_statements(date, FORM_10Q_TAG, financial_statements)

