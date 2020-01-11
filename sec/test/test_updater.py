
from sec.update_operations import SECUpdateOps
import datetime


def main():
    sec_updater = SECUpdateOps("/Users/chamanara/CompanyData/us")
    sec_updater.update_raw_quarterly_financial_statements(datetime.date(2014, 1, 1))


if __name__ == "__main__":
    main()
