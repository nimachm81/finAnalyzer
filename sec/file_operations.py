"""
Read or write financial data to folder.

"""

__all__ = ["SECFileOps"]


import os
import json
import sec.util as util

FILE_NAME_SEPARATOR = "_"
RAW_EXT = ".json"
RAW_FOLDER_NAME = "raw"
COMPANY_INFO = "company_info"
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
        file = self._create_raw_file_and_set_version_tag(file_path)
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
        file = self._create_raw_file_and_set_version_tag(file_path)
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

    def _get_saved_raw_quarterly_financial_statement_dates(self, symbol):
        self._set_curren_companny_folder(symbol)
        pass

    def _get_raw_quarterly_financial_statement(self, date):
        pass

