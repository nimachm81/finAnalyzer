"""
Read or write financial data to folder.

"""

__all__ = ["SECFileOps"]


import os
import json
import pickle
from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
import sec.util as util
import datetime

FILE_NAME_SEPARATOR = "_"
RAW_EXT = ".json"
RAW_FOLDER_NAME = "raw"
COMPANY_INFO = "company_info"
NASDAQ_SYMBOLS = "nasdaq_symbols"
FORM_10Q_TAG = "10-Q"
VERSION = 1.0


class SECFileOps:
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
    def get_version_tag():
        """Get the file tag for this version. Every raw file will start with this tag.

        returns
        --------
        :str
            version tag
        """
        version_tag = "version {}\n".format(VERSION)
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
        file.write(SECFileOps.get_version_tag())
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

    def _set_current_company_folder(self, symbol):
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
        """Creates default sub-folders inside the current company folder, if they do not already
        exist."""
        assert self.current_company_folder is not None

        # raw folder for raw (unprocessed) data
        raw_folder = os.path.join(self.current_company_folder, RAW_FOLDER_NAME)
        if not os.path.exists(raw_folder):
            os.mkdir(raw_folder)

    def _get_name_and_path_of_the_raw_financial_file(self, date, form_tag):
        """Get the name and path of the raw file containing financial statements. Assuming the
           current company folder is set up.

        parameters
        --------
        date: datetime.date
            release date of the financial statement
        form_tag: str
            financial form tag for example FORM_10Q_TAG

        returns
        --------
        :str
            file name
        :str
            absolute file path
        """
        file_name = date.isoformat() + FILE_NAME_SEPARATOR + form_tag + RAW_EXT
        file_path = os.path.join(self.current_company_folder, RAW_FOLDER_NAME, file_name)
        return file_name, file_path

    def _get_name_and_path_of_the_companyinfo_rawfile(self):
        """Get the name and path of the raw file containing company info. Assuming the
           current company folder is set up.

        returns
        --------
        :str
            file name
        :str
            absolute file path
        """
        file_name = COMPANY_INFO + RAW_EXT
        file_path = os.path.join(self.current_company_folder, RAW_FOLDER_NAME, file_name)
        return file_name, file_path

    def _write_raw_company_info(self, company_info):
        """Write raw company info to the current folder

        parameters
        --------
        company_info: str
            raw company info
        """
        file_name, file_path = self._get_name_and_path_of_the_companyinfo_rawfile()
        # file = self._create_raw_file_and_set_version_tag(file_path)
        file = open(file_path, "w")
        json.dump(company_info, file)
        file.close()

    def _write_raw_financial_statements(self, date, form_tag, financial_statements):
        """write raw financial statements to current company folder. It will be written
        in the /raw folder. The name will include the date and form tag.

        parameters
        --------
        date: datetime.date
            date of the statements
        form_tag: str
            financial form tag for example 10-Q
        financial_statements: str
            raw financial statements
        """
        file_name, file_path = self._get_name_and_path_of_the_raw_financial_file(date, form_tag)
        # file = self._create_raw_file_and_set_version_tag(file_path)
        file = open(file_path, "w")
        json.dump(financial_statements, file)
        file.close()

    def write_raw_company_info(self, symbol, company_info):
        """Write raw company info to the /raw folder

        parameters
        --------
        symbol: str
            stock symbol
        company_info: str
            raw financial statements
        """
        self._set_current_company_folder(symbol)
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
        self._set_current_company_folder(symbol)
        self._write_raw_financial_statements(date, FORM_10Q_TAG, financial_statements)

    def _remove_overhead_from_raw_file_content(self, file_content):
        """Removes the overhead from the raw file content. The overhead includes version tag
        in version 1.0 and in future versions might include other stuff.

        parameters
        --------
        file_content: str
            raw file content including overhead

        returns
        --------
        str:
            file content without overhead
        """
        first_line_end = file_content.find("\n")
        assert first_line_end > 0
        version_tag = file_content[ :first_line_end]
        assert version_tag.startswith("version")
        version_num = float(version_tag[len("version"), -1].strp())

        if version_num == 1.0:
            return file_content[first_line_end + 1: ]
        else:
            raise util.BadFileVersionError()

    def _get_dates_of_saved_raw_financial_forms(self, symbol, form_tag):
        """ Finds the dates of the saved financial forms.

        parameters
        --------
        symbol: str
            stock symbol
        form_tag: str
            financial form tag

        returns
        --------
        :list
            list of datetime.date
        """
        self._set_current_company_folder(symbol)

        date = datetime.date(2029, 1, 1)
        date_str = date.isoformat()

        file_name, file_path = self._get_name_and_path_of_the_raw_financial_file(date, form_tag)

        date_ind = file_name.find(date_str)
        assert date_ind >= 0

        # part of the file name before and after the date
        date_prefix = file_name[:date_ind]
        date_suffix = file_name[date_ind + len(date_str):]

        # look for file names containing both the date_prefix and date_suffix
        directory, _ = os.path.split(file_path)
        assert os.path.exists(directory)

        # files inside
        all_files = os.listdir(directory)

        forms = []
        for f in all_files:
            if f.find(date_prefix) >= 0 and f.find(date_suffix) >= 0:
                forms.append(f)

        dates = []
        for f in forms:
            dates.append(datetime.date.fromisoformat(f[date_ind: date_ind + len(date_str)]))

        return sorted(dates)

    def get_dates_of_saved_raw_quarterly_financial_statements(self, symbol):
        """ Finds the dates of the saved quarterly financial statements.

        parameters
        --------
        symbol: str
            stock symbol

        returns
        --------
        :list
            list of datetime.date
        """
        return self._get_dates_of_saved_raw_financial_forms(symbol, FORM_10Q_TAG)

    def get_raw_quarterly_financial_statement(self, symbol, date):
        """ opens the json file containing the 10-Q form for the specified date and returns its content.

        parameters
        --------
        symbol: str
            stock symbol
        date: datetime.date
            form release date

        returns
        --------
        :dict
            raw financial statements
        """
        self._set_current_company_folder(symbol)

        file_name, file_path = self._get_name_and_path_of_the_raw_financial_file(date, FORM_10Q_TAG)

        file = open(file_path)
        return json.load(file)

    def update_nasdaq_symbols(self):
        """ Updates Nasdaq symbols on local storage.

        returns
        --------
        : pandas.DataFrame
            nasdaq symbols
        """
        symbols = get_nasdaq_symbols()

        file_name = NASDAQ_SYMBOLS + RAW_EXT
        file_path = os.path.join(self.base_data_folder, file_name)

        file = open(file_path, "wb")
        pickle.dump(symbols, file)
        file.close()

        return symbols

    def load_nasdaq_symbols(self):
        """ Loads Nasdaq symbols from local storage.

        returns
        --------
        : pandas.DataFrame
            nasdaq symbols
        """
        file_name = NASDAQ_SYMBOLS + RAW_EXT
        file_path = os.path.join(self.base_data_folder, file_name)

        if not os.path.exists(file_path):
            self.update_nasdaq_symbols()

        file = open(file_path, "rb")
        symbols = pickle.load(file)
        file.close()

        return symbols

    def get_stored_cik(self, symbol):
        """ Find the cik number of the symbol if it is stored locally, otherwise returns None.

        parameters
        --------
        symbol: str
            company stock symbol

        returns
        --------
        :str
            cik number or None
        """
        self._set_current_company_folder(symbol)

        file_name, file_path = self._get_name_and_path_of_the_companyinfo_rawfile()

        if os.path.exists(file_path):
            file = open(file_path, "r")
            info = json.load(file)
            return info["cik"]

        else:
            return None

    def note_the_last_updated_symbol(self, symbol):
        """ Writes the last updated sumbol to file.

        parameters
        --------
        symbol: str
            stock symbol
        """
        file_name = os.path.join(self.base_data_folder, "last_updated")
        file = open(file_name, "w")
        file.write(symbol)
        file.close()

    def get_the_last_updated_symbol(self):
        """ Gets the last updated symbol if it is stored in local file.

        returns
        --------
        :str
            last updated symbol
        """
        file_name = os.path.join(self.base_data_folder, "last_updated")
        if os.path.exists(file_name):
            file = open(file_name, "r")
            symbol = file.read()
            file.close()
            return symbol
        else:
            return None

    def get_all_folders(self):
        """ Gets a list of ll folders. Each folder represents a stock symbol.

        returns
        --------
        :list
            list of all subdirectories
        """
        folder_content = os.listdir(self.base_data_folder)

        folders = [f for f in folder_content if os.path.isdir(os.path.join(self.base_data_folder, f))]

        return sorted(folders)


