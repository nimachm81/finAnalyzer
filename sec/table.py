"""
data structure for representing an HTML table

"""

__all__ = ["CellType", "Cell", "Row", "Table"]

from enum import Enum
import re


class CellType(Enum):
    NORMAL = 0
    HEADER = 1


class Cell:
    """
    Represents a cell in the table. A given cell can span multiple rows and columns.
    """
    def __init__(self, row_span=1, col_span=1, cell_type=CellType.NORMAL):
        """
        :param row_span:    number of rows spanned by the cell.
        :param col_span:    number of columns spanned by the cell.
        :param cell_type:   normal or header cell
        """
        self.type = cell_type
        self.row_span = row_span
        self.col_span = col_span
        self.data = None

        # when a cell spans multiple rows, the first row will keep the actual cell
        # while all the cells below the first row (and belonging to the same multi-row cell) get a link to
        # the actual cell, and their data will be set to None
        self.linked_cell = None

    def set_data(self, data):
        """
        Set the data field of the cell.

        :param data:        cell data. Could take any data type.
        :return:
        """
        self.data = data

    def get_data(self):
        """
        Get the cell data

        :return:            cell data
        """
        return self.data

    def get_type(self):
        """
        Get the cell type

        :return:            cell type: normal or header
        """
        return self.type

    def get_row_span(self):
        """
        Get the cell's row span

        :return:            (int) number of row spans
        """
        return self.row_span

    def get_col_span(self):
        """
        Get the number of column spans.

        :return:            (int) number of column spans
        """
        return self.col_span

    def link_to_cell(self, cell):
        """
        Keeps a link to the cell, and sets the data to None. It is assumed that the link keeps the data

        :param cell:        cell to link to
        :return:
        """
        self.data = None
        self.linked_cell = cell

    def get_linked_cell(self):
        """
        Get the linked cell. For multi-row cells the first row gets a copy of the cell while the rest get a link
        to that top cell.

        :return:            linked cell (or None if it is not linked)
        """
        return self.linked_cell

    def is_linked_cell(self):
        """
        :return:            True/False for linked/not linked
        """
        if self.linked_cell is not None:
            assert data is None
            return True
        else:
            return False


class Row:
    """
    Represents a table row. A row is basically a list of cells.
    """
    def __init__(self):
        self.cells = []

    def append_cell(self, cell):
        """
        Adds a cell at the end of the row.

        :param cell:        (Cell) the cell to be appended to the row
        :return:
        """
        self.cells.append(cell)

    def get_num_of_cells(self):
        """
        Get the total number of cells.

        :return:            (int) number of cells
        """
        return len(self.cells)

    def get_cell_data(self, cell_index):
        """
        Get the cell data at the given cell index.

        :param cell_index:      cell index
        :return:                cell data
        """
        assert cell_index < self.get_num_of_cells()
        return self.cells[cell_index].get_data()

    def is_linked_cell(self, cell_index):
        """
        Whether or not the given cell index is linked to another cell.
        :param cell_index:      cell index
        :return:
        """
        return self.cells[cell_index].is_linked_cell()

    def print(self):
        """
        Prints the cells data separated by white space
        :return:
        """
        for cell in self.cells:
            print(cell.get_data(), end="        ")
        print()


class Table:
    def __init__(self):
        self.rows = []
        self.rows_linked = None

    def appendRow(self, row):
        """
        Append row at the back of the rows list

        :param row:         Row object
        :return:
        """
        self.rows.append(row)

    def _htmlrow_to_rowobj(self, html_row):
        """
        Take a string representing a html row and represent it as a Row object. It ignores previous multi-row cell
        information and directly translates the string between <tr> .. </tr> to a Row object.


        :param html_row:        html string between <tr> .. </tr>
        :return:                a Row object representing that row
        """
        row = Row()

        # find the expressions between <td...</td>   or  <th...</th> it does not consume the tags themselves
        # (only returns ... )
        td_th_tag_pairs = re.findall("((?<=<td).*?(?=</td>))|((?<=<th).*?(?=</th>))", html_row)

        for s_td, s_th in td_th_tag_pairs:
            assert len(s_td) == 0 or len(s_th) == 0
            if len(s_th) > 0:
                assert len(s_td) == 0

                rowspan, colspan = self._get_span_options(s_th)
                cell_type = CellType.HEADER

                assert s_th.find(">") >= 0
                cell_data = s_th[s_th.find(">") + 1:].strip()

                cell = Cell(rowspan, colspan, cell_type)
                cell.set_data(cell_data)

                row.append_cell(cell)

            else:
                assert len(s_th) == 0
                # th tag
                assert len(s_td) > 0

                rowspan, colspan = self._get_span_options(s_td)
                cell_type = CellType.NORMAL

                assert s_td.find(">") >= 0
                cell_data = s_td[s_td.find(">") + 1:].strip()

                cell = Cell(rowspan, colspan, cell_type)
                cell.set_data(cell_data)

                row.append_cell(cell)

        return row

    def _get_span_options(self, options_str):
        """
        Extracts the rowspan and colspan from the options_str

        :param options_str:     <td> or <th> options -->  <td options_str> or <th options_str>
        :return:                rowspan and colspan as integers
        """
        rowspan = 1
        if options_str.find("rowspan:") >= 0:
            rowspan = re.findall("(?<=rowspan:)\s*[0-9]+(?=[^%d])", options_str)
            assert len(rowspan) == 1
            rowspan = int(rowspan[0].strip())
        assert rowspan >= 1

        colspan = 1
        if options_str.find("colspan:") >= 0:
            colspan = re.findall("(?<=colspan:)\s*[0-9]+(?=[^%d])", options_str)
            assert len(colspan) == 1
            colspan = int(colspan[0].strip())
        assert colspan >= 1

        return rowspan, colspan

    def read_tablecontent(self, table_content):
        """
        Processes the table content into a table, consisting a list of Row objects. Ignores links for multi-row cells
        (links will be constructed later and stored in self.rows_linked)

        :param table_content:       html string of the table content
        :return:
        """
        rows_str = re.findall("<tr.*?</tr>", table_content)

        for row_str in rows_str:
            self.appendRow(self._htmlrow_to_rowobj(row_str))

    def print(self):
        """
        Prints the table rows
        :return:
        """
        for row in self.rows:
            row.print()