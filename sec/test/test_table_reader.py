

import datetime
from sec.financial_tables import SECTableReader
from sec.file_operations import SECFileOps
from sec.table_processor.tables10Q import Tables10Q


def get_stock_10q_tables(symbol, date=None):
    sec_tables = SECTableReader("/Users/chamanara/CompanyData/us")

    if date is None:
        dates = sec_tables.get_quarterly_report_dates(symbol)
        if len(dates) > 0:
            date = dates[-1]

    if date is not None:
        print(symbol, date, end="  ")
        tables = sec_tables.get_quarterly_report_tables(symbol, date)
        print(tables)
        print(symbol, date, tables.keys())
        return Tables10Q(tables)


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
    # no SOP or SOI: [['AMP', datetime.date(2018, 11, 5)], ['ARES', datetime.date(2014, 6, 10)], ['BSX', datetime.date(2019, 4, 29)], ['CIR', datetime.date(2019, 8, 1)], ['CIR', datetime.date(2019, 11, 13)], ['CVNA', datetime.date(2017, 6, 6)], ['CWH', datetime.date(2016, 11, 10)], ['DX', datetime.date(2019, 5, 3)], ['EGRX', datetime.date(2019, 5, 7)], ['EIG', datetime.date(2015, 4, 30)], ['EVA', datetime.date(2015, 6, 8)], ['FG', datetime.date(2018, 5, 9)], ['FG', datetime.date(2018, 8, 9)], ['FG', datetime.date(2018, 11, 7)], ['FG', datetime.date(2019, 5, 7)], ['FG', datetime.date(2019, 8, 7)], ['FG', datetime.date(2019, 11, 6)], ['FOCS', datetime.date(2018, 8, 28)], ['GYRO', datetime.date(2016, 5, 13)], ['GYRO', datetime.date(2016, 8, 10)], ['GYRO', datetime.date(2016, 11, 14)], ['GYRO', datetime.date(2017, 5, 11)], ['GYRO', datetime.date(2017, 8, 10)], ['GYRO', datetime.date(2017, 11, 9)], ['GYRO', datetime.date(2018, 5, 11)], ['GYRO', datetime.date(2018, 8, 9)], ['GYRO', datetime.date(2018, 11, 9)], ['GYRO', datetime.date(2019, 5, 10)], ['GYRO', datetime.date(2019, 8, 14)], ['GYRO', datetime.date(2019, 11, 14)], ['HGH', datetime.date(2019, 8, 1)], ['HGH', datetime.date(2019, 11, 4)], ['HIG', datetime.date(2019, 8, 1)], ['HIG', datetime.date(2019, 11, 4)], ['JCP', datetime.date(2019, 8, 28)], ['JLL', datetime.date(2019, 8, 7)], ['JLL', datetime.date(2019, 11, 6)], ['KN', datetime.date(2019, 7, 31)], ['KN', datetime.date(2019, 10, 28)]]
    tables_10q = get_stock_10q_tables("amd", date=None)
    for title, table in tables_10q.tables.items():
        print("="*100)
        table.print(linked=True)
        col_titles = table.get_column_titles()
        print(col_titles)
    tables_10q.get_net_income()

    # print_qurterly_table_titles()


if __name__ == "__main__":
    main()
