"""
Update company financial data

"""

__all__ = ["SECUpdateOps"]

import os
from sec.file_operations import SECFileOps
from sec.web_reader import SECWebReader
from sec.util import SymbolNotFoundError, PageLoadError
import time


class SECUpdateOps:
    def __init__(self, data_folder):
        self.sec_file_ops = SECFileOps(data_folder)
        self.sec_web_reader = SECWebReader()

    def _update_raw_quarterly_financial_statements(self, symbol, last_date):
        """ Download and store raw quarterly statements going back to last_date. It
        overwrites previously stored files if any.

        parameters
        --------
        symbol: str
            company symbol
        last_date: datetime.date
            find reports until this date
        """
        cik_stored = self.sec_file_ops.get_stored_cik(symbol)
        print("cik_stored: ", cik_stored)

        reports = self.sec_web_reader.find_quarterly_reports_until_date(symbol, last_date, cik_stored)
        company_info = reports["info"]
        company_docs = reports["docs"]

        cik = company_info["cik"]
        if cik_stored:
            assert int(cik) == int(cik_stored)

        self.sec_file_ops.write_raw_company_info(symbol, company_info)

        # already downloaded
        stored_dates = self.sec_file_ops.get_dates_of_saved_raw_quarterly_financial_statements(symbol)

        for doc_info in company_docs:
            file_date = doc_info["date"]
            if doc_info["is_interactive"]:
                acc_num = doc_info["acc_num"]

                if file_date in stored_dates:
                    print("Data for {}  cik: {}  date: {} already exists. skipping..".format(symbol, cik, file_date))
                    continue

                if file_date < last_date:
                    continue

                financial_statements = \
                    self.sec_web_reader.get_raw_quarterly_financial_statements(cik, acc_num)

                self.sec_file_ops.write_raw_quarterly_10Q_financial_statements\
                    (symbol, file_date, financial_statements)
            else:
                print("No interactive page for {}  cik: {}  date: {}".format(symbol, cik, file_date))

    def get_nasdaq_stock_symbols(self, update=False):
        """ Get Nasdaq symbols from local storage.

        parameters
        --------
        update: boolean
            Update the symbols from the nasdaq website
        returns
        --------
        :pandas.DataFrame
            List of stock symbols and related information
        """
        if update:
            self.sec_file_ops.update_nasdaq_symbols()

        symbols = self.sec_file_ops.load_nasdaq_symbols()

        # @todo: convention: convert symbol names to uppercase
        return symbols

    def update_raw_quarterly_financial_statements(self, last_date):
        """ Download and store raw quarterly statements going back to last_date. It
                skips previously stored files if any.

            parameters
            --------
            last_date: datetime.date
                find reports until this date
        """
        # get the last updated symbol
        last_symbol = self.sec_file_ops.get_the_last_updated_symbol()
        print("last updated symbol: ", last_symbol)

        symbols_df = self.get_nasdaq_stock_symbols()    # pandas.Dataframe
        symbols = symbols_df.index.tolist()

        # get the last updated symbol index
        last_symbol_index = 0
        if last_symbol:
            last_symbol_index = symbols.index(last_symbol)

        i = -1
        n_symb = len(symbols_df)
        for index, row in symbols_df.iterrows():
            i += 1

            # pick up updating after the last updated symbol
            if i < last_symbol_index:
                continue

            time.sleep(10)
            print("{}/{}     {}  -   ETF: {}".format(i, n_symb, index, row['ETF']))
            if not row['ETF']:
                try:
                    self._update_raw_quarterly_financial_statements(index, last_date)
                except SymbolNotFoundError:
                    print("SEC: Symbol not found {}".format(index))
                except PageLoadError:
                    print("Error loading page {}".format(index))
                else:
                    self.sec_file_ops.note_the_last_updated_symbol(index)
                    if i == n_symb:
                        self.sec_file_ops.note_the_last_updated_symbol(symbols[0])
            time.sleep(20)
