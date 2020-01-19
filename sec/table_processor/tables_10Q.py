"""
Processes 10-Q tables
"""

from sec.table import Table, CellType
from sec.util import CorruptDaraError


class Tables_10Q:
    def __init__(self, tables):
        self.tables = tables
        self.statement_of_operation_table = self._find_statement_of_operation_table()
        self.statement_of_income_table = self._find_statement_of_income_table()
        self.balanced_sheet_table = self._find_balance_sheet_table()

    def _find_statement_of_operation_table(self):
        """ Searches inside the titles and tries to find the table that corresponds to statement of operations

        :return: (Table)            the table corresponding to statement of operation or None if it was not found
        """
        for title in tables.keys():
            title = title.lower()
            if "statement" in title and "operation" in title and "parenthetical" not in title:
                return self.tables[title]
        return None

    def _find_statement_of_income_table(self):
        """ Searches inside the titles and tries to find the table that corresponds to statement of income

        :return: (Table)            the table corresponding to statement of income or None if it was not found
        """
        for title in tables.keys():
            title = title.lower()
            if "statement" in title and ("income" in title or "earning" in title or "loss" in title) \
                    and "parenthetical" not in title:
                return self.tables[title]
        return None

    def _find_balance_sheet_table(self):
        """ Searches inside the titles and tries to find the table that corresponds to balance sheets

        :return: (Table)            the table corresponding to balance sheets or None if it was not found
        """
        for title in tables.keys():
            title = title.lower()
            if "sheet" in title and "balance" in title and "parenthetical" not in title:
                return self.tables[title]
        return None

    def get_net_income(self):
        pass

    def get_total_assets(self):
        pass

    def get_total_revenue(self):
        pass

    def get_total_shares(self):
        pass


