

import datetime
from sec.financial_tables import SECTableReader
from sec.file_operations import SECFileOps


def get_stock_tables(symbol, date=None):
    sec_tables = SECTableReader("/Users/chamanara/CompanyData/us")

    if date is None:
        dates = sec_tables.get_quarterly_report_dates(symbol)
        date = dates[-1]

    if date is not None:
        print(symbol, date, end="  ")
        tables = sec_tables.get_quarterly_report_tables(symbol, date)
        print(tables)
        print(symbol, date, tables.keys())


def print_qurterly_table_titles():
    sec_tables = SECTableReader("/Users/chamanara/CompanyData/us")
    file_ops = SECFileOps("/Users/chamanara/CompanyData/us")

    symbols = file_ops.get_stored_nasdaq_symbols().index

    print(symbols)

    corrupt_data = []
    no_statement_of_operation = []
    no_statement_of_income = []
    no_statement_of_operation_or_income = []

    for symbol in symbols:
        dates = sec_tables.get_quarterly_report_dates(symbol)
        for date in dates:
            print(symbol, date, end="  \n")
            try:
                tables = sec_tables.get_quarterly_report_tables(symbol, date)
                # print(tables.keys())
                statement_of_operation_found = False
                for title in tables.keys():
                    title = title.lower()
                    if "statement" in title and "operation" in title and "parenthetical" not in title:
                        print("SOP: ", title)
                        statement_of_operation_found = True
                statement_of_income_found = False
                for title in tables.keys():
                    title = title.lower()
                    if "statement" in title and ("income" in title or "earning" in title or "loss" in title) \
                            and "parenthetical" not in title:
                        print("SOI: ", title)
                        statement_of_income_found = True

                if not statement_of_operation_found:
                    no_statement_of_operation.append([symbol, date])
                if not statement_of_income_found:
                    no_statement_of_income.append([symbol, date])
                if not (statement_of_income_found or statement_of_operation_found):
                    no_statement_of_operation_or_income.append([symbol, date])
            except:
                corrupt_data.append([symbol, date])

    print("corrupt_data: ", corrupt_data)
    print("no_statement_of_operation: ", no_statement_of_operation)
    print("no_statement_of_income: ", no_statement_of_income)
    print("no_statement_of_operation_or_income: ", no_statement_of_operation_or_income)


def main():
    # get_stock_tables("aegn", datetime.date(2019, 5, 3))
    print_qurterly_table_titles()


if __name__ == "__main__":
    main()
