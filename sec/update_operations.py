"""
Update company financial data

"""

__all__ = ["SECUpdateOps"]

import os
from sec.file_operations import SECFileOps
from sec.web_reader import SECWebReader


class SECUpdateOps:
    def __init__(self, data_folder):
        self.sec_file_ops = SECFileOps(data_folder)
        self.sec_web_reader = SECWebReader()

    def download_raw_quarterly_financial_statements(self, symbol, last_date):
        """ Download and store raw quarterly statements going back to last_date. It
        overwrites previously stored files if any.

        parameters
        --------
        symbol: str
            company symbol
        last_date: datetime.date
            find reports until this date
        """
        reports = self.sec_web_reader.find_quarterly_reports_until_date(symbol, last_date)
        company_info = reports["info"]
        company_docs = reports["docs"]

        cik = company_info["cik"]

        self.sec_file_ops.write_raw_company_info(symbol, company_info)

        for doc_info in company_docs:
            if doc_info["is_interactive"]:
                acc_num = doc_info["acc_num"]
                file_date = doc_info["date"]
                financial_statements = \
                    self.sec_web_reader.get_raw_quarterly_financial_statements(cik, acc_num)

                self.sec_file_ops.write_raw_quarterly_10Q_financial_statements\
                    (symbol, file_date, financial_statements)


