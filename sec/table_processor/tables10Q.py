"""
Processes 10-Q tables
"""

__all__ = ["Tables10Q"]

from sec.table import Table, CellType
from sec.util import CorruptDaraError


class Tables10Q:
    def __init__(self, tables):
        self.tables = tables
        self.statement_of_operation_table = self._find_statement_of_operation_table()
        self.statement_of_income_table = self._find_statement_of_income_table()
        self.balanced_sheet_table = self._find_balance_sheet_table()

    def _find_statement_of_operation_table(self):
        """ Searches inside the titles and tries to find the table that corresponds to statement of operations

        :return: (Table)            the table corresponding to statement of operation or None if it was not found
        """
        for title in self.tables.keys():
            title_lc = title.lower()
            if "statement" in title_lc and "operation" in title_lc and "parenthetical" not in title_lc:
                return self.tables[title]
        return None

    def _find_statement_of_income_table(self):
        """ Searches inside the titles and tries to find the table that corresponds to statement of income

        :return: (Table)            the table corresponding to statement of income or None if it was not found
        """
        for title in self.tables.keys():
            title_lc = title.lower()
            if "statement" in title_lc and ("income" in title_lc or "earning" in title_lc or "loss" in title_lc) \
                    and "parenthetical" not in title_lc:
                return self.tables[title]
        return None

    def _find_balance_sheet_table(self):
        """ Searches inside the titles and tries to find the table that corresponds to balance sheets

        :return: (Table)            the table corresponding to balance sheets or None if it was not found
        """
        for title in self.tables.keys():
            title_lc = title.lower()
            if "sheet" in title_lc and "balance" in title_lc and "parenthetical" not in title_lc:
                return self.tables[title]
        return None

    def get_net_income(self):
        """
        It tries to find the net income
        :return:
        """
        if self.statement_of_income_table:
            rows_net_income = self.statement_of_income_table.find_rows_with_keywords(has=["net", "income"])
            for row in rows_net_income:
                row.print()
        elif self.statement_of_operation_table:
            rows_net_income = self.statement_of_operation_table.find_rows_with_keywords(has=["net", "income"])
            for row in rows_net_income:
                row.print()

    def get_total_assets(self):
        pass

    def get_total_revenue(self):
        pass

    def get_total_shares(self):
        pass


