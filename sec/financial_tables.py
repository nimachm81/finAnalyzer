"""
Read raw financial data and convert them to formatted data tables

"""

__all__ = ["SECTableReader"]


from sec.file_operations import SECFileOps
from sec.table import Table

from html.parser import HTMLParser


class RawTableCleaner(HTMLParser):
    """
    This class is used to remove noise attributes and unwanted data from html tags
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.table = ""

    def clear_table(self):
        """ Clear the table """
        self.table = ""

    def _get_attribute_dic(self, attrs):
        """Put the attributes in dictionary format. They are originally in a list containing tuple pairs.

        returns
        --------
        :dict
            attributes
        """
        attr_dic = {}
        for attr_pair in attrs:
            attr_dic[attr_pair[0]] = attr_pair[1]
        return attr_dic

    def handle_starttag(self, tag, attrs):
        """Keep only td, tr and th tags, and only the rowspan and colspan attributes"""
        if tag in ["td", "tr", "th"]:
            attr_dic = self._get_attribute_dic(attrs)
            attr = ""
            for att in attr_dic:
                if att in ["rowspan", "colspan"]:
                    attr += ' {}:{} '.format(att, attr_dic[att])

            self.table += "<{}{}>".format(tag, attr)
            # print("<{}{}>".format(tag, attr), end="    ")

    def handle_endtag(self, tag):
        """Keep only the td, tr and th tags."""
        if tag in ["td", "tr", "th"]:
            self.table += "</{}>".format(tag)
            # print("</{}>".format(tag))

    def handle_data(self, data):
        """Strip the white spaces at the front and back of each data."""
        if len(data.strip()) > 0:
            self.table += data
            # print(data, end="    ")


class SECTableReader:
    """
    It extracts readable tables from saved financial statemments
    """
    def __init__(self, data_folder):
        self.sec_file_ops = SECFileOps(data_folder)

        folders = self.sec_file_ops.get_all_folders()
        # print("folders: \n", folders)

    def _extract_raw_table(self, expr):
        """ Extracts the string between "<table" and "/table>" i.e. the table from the raw html data.

        parameters
        --------
        expr: str
            raw input html data

        returns
        --------
        :str
            table part of the raw html data
        """
        str_start = "<table"
        str_end = "/table>"

        ind_start = expr.find(str_start)
        assert ind_start >= 0

        ind_end = expr.find(str_end)
        assert ind_end >= 0

        return expr[ind_start: ind_end + len(str_end)]

    def _remove_unnecessary_tags(self, raw_data):
        """ Extracts the rarw table, removes parasitic tags and keeps useful table data.

        parameter
        --------
        raw_data: str
            raw table data

        returns
        --------
        :str
            useful table data with unwanted tags removed
        """
        parser = RawTableCleaner()
        parser.clear_table()

        table = self._extract_raw_table(raw_data)

        parser.feed(table)

        return parser.table

    def get_quarterly_report_dates(self, symbol):
        """It finds the dates of the saved quarterly reports

        parameters
        --------
        symbol: str
            the stock symbol

        returns
        --------
        : list
            reported dates
        """
        return self.sec_file_ops.get_dates_of_saved_raw_quarterly_financial_statements(symbol)

    def get_quarterly_report_tables(self, symbol, date):
        """ It extracts the quarterly report tables for the given symbol at the given date

        parameters
        --------
        symbol: str
            the stock symbol
        date: datetime.date
            the report date

        returns
        --------
        : dict
            {statement_title: table}
        """
        raw_data = self.sec_file_ops.get_raw_quarterly_financial_statement(symbol, date)

        cleared_tables = {}
        for title in raw_data:
            cleared_tables[title] = self._remove_unnecessary_tags(raw_data[title])
        # print(cleared_tables)

        tables = {}
        for title in cleared_tables:
            table = Table()
            table.read_tablecontent(cleared_tables[title])
            tables[title] = table

        for title in tables:
            tables[title].setup_linked_rows()
            # tables[title].print(linked=True)

        return tables
