"""
data structure for representing an HTML table

"""

__all__ = ["CellType", "Cell", "Row", "Table"]

from enum import Enum
import re
import numpy as np


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
        self.type = cell.type
        self.row_span = cell.row_span
        self.col_span = cell.col_span
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
            assert self.data is None
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

        :param cell:(Cell)      the cell to be appended to the row
        :return:
        """
        self.cells.append(cell)

    def get_num_of_cells(self):
        """
        Get the total number of cells.

        :return:(int)           number of cells
        """
        return len(self.cells)

    def get_cell(self, cell_index):
        """
        Get the Cell object corresponding to cell_index

        :param cell_index:(int)     index of the cell
        :return:(Cell)              cell at the cell_index
        """
        assert cell_index < self.get_num_of_cells()
        return self.cells[cell_index]

    def get_cell_data(self, cell_index):
        """
        Get the cell data at the given cell index.

        :param cell_index:      cell index
        :return:                cell data
        """
        assert cell_index < self.get_num_of_cells()
        return self.cells[cell_index].get_data()

    def get_row_span(self, cell_index):
        """
        Get the row span for the given cell

        :param cell_index: (int)        the cell index
        :return: (int)                  row span
        """
        assert cell_index < self.get_num_of_cells()
        return self.cells[cell_index].get_row_span()

    def get_col_span(self, cell_index):
        """
        Get the column span for the given cell

        :param cell_index: (int)        the cell index
        :return: (int)                  column span
        """
        assert cell_index < self.get_num_of_cells()
        return self.cells[cell_index].get_col_span()

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
            if not cell.is_linked_cell():
                print(cell.get_data(), end="        ")
            else:
                print("--------", end="        ")
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

    def get_num_of_rows(self):
        """
        Get the number of rows
        :return: (int)          number of rows
        """
        return len(self.rows)

    def get_num_of_columns(self):
        """
        The number of columns are extracted from the first row.

        :return: (int)        number of columns
        """
        num_col = 0

        if len(self.rows) > 0:
            row_0 = self.rows[0]

            n_cells = row_0.get_num_of_cells()

            for i in range(n_cells):
                num_col += row_0.get_col_span(i)

        return num_col

    def setup_linked_rows(self):
        """
        Sets up linked rows: multi-row cells are copied to the rows beneath in the form of linked_cells i.e.
        the corresponding cell in the following row keeps a copy of the cell above and sets its own data to None
        :return:
        """
        num_row = len(self.rows)
        num_col = self.get_num_of_columns()
        self.rows_linked = []

        # multi-row structure
        # if a row extends to multiple rows the corresponding cells in the next rows will be marked by a number
        # n >= 0, and link_indices[n] = (row_ind, cell_ind) corresponding to the row and cell indices of the linked
        # cell. If a column is not liked to any previous rows it is marked -1. If it is occupied by previous rows
        # but it is not the first column of the cell it will be marked -2.
        multi_row_struct = -np.ones((num_row, num_col), dtype=int)
        link_indices = []

        for i in range(len(self.rows)):
            row_i = self.rows[i]
            row_link_i = Row()

            ind_col = 0

            # if the multi_row_struct at this row starts with a non-negative number it means the first cell
            # is a linked cell
            if multi_row_struct[i, ind_col] >= 0:
                assert  multi_row_struct[i, ind_col] < len(link_indices)
                cell = Cell()
                # rrow and cell index to link to
                link_r, link_c = link_indices[multi_row_struct[i, ind_col]]
                cell.link_to_cell(self.rows[link_r].get_cell(link_c))
                row_link_i.append_cell(cell)

            # increase the column index if the first few columns are linked
            for j in range(num_col):
                if multi_row_struct[i, j] == -1:
                    break
                else:
                    ind_col += 1

            # for each cell
            for j in range(row_i.get_num_of_cells()):
                # if it is a multi-row cell mark all the columns below the cell as linked columns (the first column is
                # marked linked i.e. >=0 and the rest are marked to be  part of the first column i.e. -2)
                if row_i.get_row_span(j) > 1:
                    link_indices.append((i, j))          # ---> linked to row i cell j
                    for p in range(1, row_i.get_row_span(j)):
                        for q in range(row_i.get_col_span(j)):
                            if q == 0:
                                # check this index in link_indices to see which row and column to link to
                                multi_row_struct[i + p, ind_col + q] = len(link_indices) - 1
                            else:
                                multi_row_struct[i + p, ind_col + q] = -2

                # add the next cell if it is a normal cell
                if multi_row_struct[i, ind_col] == -1:
                    row_link_i.append_cell(row_i.get_cell(j))
                # otherwise (it is a linked cell) create a linked cell
                else:
                    assert 0 <= multi_row_struct[i, ind_col] < len(link_indices)
                    cell = Cell()
                    # rrow and cell index to link to
                    link_r, link_c = link_indices[multi_row_struct[i, ind_col]]
                    cell.link_to_cell(self.rows[link_r].get_cell(link_c))
                    row_link_i.append_cell(cell)

                ind_col += row_i.get_col_span(j)

                # adjust the column index based on the next column data i.e. increase it if the next one is linked
                for k in range(ind_col, num_col):
                    if multi_row_struct[i, k] == -1:
                        break
                    else:
                        ind_col += 1

            assert ind_col == num_col
            self.rows_linked.append(row_link_i)

        print(multi_row_struct)
        print(link_indices)

    def print(self, linked=False):
        """
        Prints the table rows
        :param linked:(Boolean)     Print the linked cells
        :return:
        """
        if not linked:
            for row in self.rows:
                row.print()
        else:
            for row in self.rows_linked:
                row.print()

