"""
Reading US companies financial data from SEC.gov

"""

__all__ = ["SECWebReader"]

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import os
import datetime
import time
import sec.util as util


class SECWebReader:
    """Reads, stores and updates US stock financial data from sec.gov. 
    """
    
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.url_base = "https://www.sec.gov"

    def _open_url_with_retry(self, url, timeout=10, num_retry=3, timeout_grow_factor=2.0):
        """tries to open the url wirh the requested number of retries. raises PageLoadError
        if failed after multiple retries.

        parameters
        --------
        url: str
        timeout: int
            timeout in seconds
        num_retry: int
            number of retries
        timeout_grow_factor: float
            the timeout grows by this factor on each retry
        """
        self.driver.set_page_load_timeout(timeout)
        n_tries = 0

        while True:
            try:
                self.driver.get(url)
            except TimeoutException:
                print("Page timed out")
                n_tries += 1
                timeout *= timeout_grow_factor
                self.driver.set_page_load_timeout(timeout)
                if n_tries > num_retry:
                    raise util.PageLoadError()
            else:
                break

    def _search_company_ticker(self, stock_symbol):
        """Opens a browser page to the SEC's Edgar's company search page and look's 
        up the stock symbol.
        
        parameters
        --------
        stock_symbol: str
            stock symbol or ticker
        """
        url = self.url_base + \
            "/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&Find=Search".\
            format(stock_symbol)

        self._open_url_with_retry(url)
    
        h1_tags = self.driver.find_elements_by_tag_name("h1")
        if len(h1_tags) > 0:
            if h1_tags[0].get_attribute("innerHTML").startswith("No matching Ticker Symbol."):
                raise util.SymbolNotFoundError

    def _search_financial_forms_by_cik(self, cik, form_type):
        """Opens a browser page to the SEC's Edgar's company search page and searches for the specified form type.

        parameters
        --------
        cik: str
            CIK number of the company
        form_type: str
            financial form type (for example "10-Q")
        """
        url = self.url_base + \
            "/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb=&owner=exclude&count=100".\
            format(cik, form_type)

        self._open_url_with_retry(url)

        h1_tags = self.driver.find_elements_by_tag_name("h1")
        if len(h1_tags) > 0:
            if h1_tags[0].get_attribute("innerHTML").startswith("No matching CIK."):
                raise util.SymbolNotFoundError

    def _click_next_page(self):
        """On the company documents page finds and clicks the next button.
        
        returns
        ----------
        bool
            true if found the next button, false if the next button is not on the 
            page, normally meaning last page. 
            
        """
        butt_next = self.driver.find_elements_by_xpath("//input[@value='Next 40']")
        if len(butt_next) > 0:
            butt_next[0].click()
            return True
        else:
            return False
    
    def _find_quarterly_financial_reports_on_docs_page(self):
        """Assuming the company documents list page is open, it searches through the table
        for 10-Q forms and finds their dates and description (description includes 
        accession number). It also finds the company info including its CIK number. 
        The CIK and accession numbers can then be used to retrieve 10-Q forms.
        
        returns
        ----------
        company_info_and_docs: dict
            contains company info, address, and all 10-Q financial doc information found on the
            current web page.
            
        """
        content_div = self.driver.find_element_by_id("contentDiv")
        
        company_info_elems = content_div.find_elements_by_class_name("companyInfo")
        company_address_elems = content_div.find_elements_by_class_name("mailer")
        
        company_info_and_docs = {}
        assert len(company_info_elems) > 0
        company_info_and_docs["info"] = company_info_elems[0].get_attribute("innerHTML")
            
        if len(company_address_elems) > 0:
            company_info_and_docs["address"] = company_address_elems[0].get_attribute("innerHTML")
        
        table = content_div.find_element_by_class_name("tableFile2")
        table.get_attribute('innerHTML')
        
        rows = table.find_elements_by_xpath("tbody/*")
        
        # find dates and accession numbers for 10-Q forms
        forms_10Q_data = []
        
        for i in range(1, len(rows)):
            row = rows[i]
            cols = row.find_elements_by_xpath("*")
            assert len(cols) == 5
            if cols[0].get_attribute('innerHTML') == "10-Q":
                date = cols[3].get_attribute('innerHTML')
                description = cols[2].get_attribute('innerHTML')
                interactive_data_link = cols[1].find_elements_by_id("interactiveDataBtn")
                is_interactive = False
                if len(interactive_data_link) > 0:
                    is_interactive = True
                
                forms_10Q_data.append({"date": date,
                                       "description": description,
                                       "is_interactive": is_interactive})
    
        company_info_and_docs["forms_10Q"] = forms_10Q_data
        
        return company_info_and_docs

    def _find_raw_quarterly_reports_until_date(self, stock_symbol, date, cik=None):
        """It searches the stock symbol, finds its documents and retrieves the raw information
        on the 10-Q forms until the specified date. Raw meaning the strings contain the information
        but need to be processed to get the data.
        
        parameters
        ----------
        stock_symbol: str
            The symbol of the stock to search for.
        date: datetime.date
            Find documents going back to this date.
        cik: str (optional)
            CIK number. If provided it will be used instead of stock_symbol.
            
        returns
        ----------
        : dict
            contains company info, and 10-Q form dates and descriptions.
            
        """
        # @todo: wait until elements are available instead of hard wait times
        if cik is None:
            self._search_company_ticker(stock_symbol)

            time.sleep(5)
            cik = self._get_cik_number(self._find_quarterly_financial_reports_on_docs_page()["info"])

        self._search_financial_forms_by_cik(cik, "10-Q")
        time.sleep(5)

        company_info_and_docs = None
        
        while True:
            company_info_on_this_page = self._find_quarterly_financial_reports_on_docs_page()
            time.sleep(5)
            
            if company_info_and_docs is None:
                company_info_and_docs = {"info": company_info_on_this_page["info"],
                                         "docs": company_info_on_this_page["forms_10Q"]}
                
            else:
                company_info_and_docs["docs"].extend(company_info_on_this_page["forms_10Q"])

            # break if passed the date
            if len(company_info_and_docs["docs"]) > 0:
                last_date = company_info_and_docs["docs"][-1]["date"]
                if datetime.date.fromisoformat(last_date) < date:
                    break
            
            # move to the next page
            last_page = not self._click_next_page()
            time.sleep(5)
            
            if last_page:
                break
            
        return company_info_and_docs

    def _get_accession_number(self, doc_description):
        """It retrieves the accession number from the document description string.
        
        parameters
        ----------        
        doc_description: str
            financial document desciprion found in the third column of the
            company documents table in EDGAR company search page, which is 
            returned by the function _find_quarterly_financial_reports_on_docs_page.
            
        returns
        ----------
        str
            accession number.
            
        """
        print("doc_description: ", doc_description)
        access_num = None
        try:
            access_num = util.extract_text_between_expressions(doc_description, "Acc-no:", "&nbsp")
        except AssertionError:
            access_num = util.extract_text_between_expressions(doc_description, "Acc-no: ", " ")

        access_num = access_num.strip()
        assert len(access_num) == 20
        
        return access_num
    
    def _get_cik_number(self, company_info):
        """It retreives the CIK number out of the company info string.
        
        parameters
        ----------
        company_info: str
            The company info string on top of the EDGAR's company documents page, 
            returned by _find_quarterly_financial_reports_on_docs_page.
            
        returns
        ----------
        str 
            CIK number.
        """
        cik_num = util.extract_text_between_expressions(company_info, "CIK=", "&amp")
        
        return cik_num.strip()
    
    def _process_company_info_and_docs(self, company_info_and_docs):
        """It finds the CIK number and the accession numbers for all the input financial docs.
        
        parameters
        --------
        company_info_and_docs: dict
            includes company info and address as raw string, as well as raw financial documents 
            description.
            
        returns
        --------
        dict
            processed data including CIK number of the company and accession numbers of the financial
            documents.
        """
        company_info_and_docs_processed = {"info": {"cik": self._get_cik_number(company_info_and_docs["info"])},
                                           "docs": []}

        docs = company_info_and_docs["docs"]
        processed_docs = company_info_and_docs_processed["docs"]
        
        for i in range(len(docs)):
            processed_docs.append({"date": datetime.date.fromisoformat(docs[i]["date"]),
                                   "acc_num": self._get_accession_number(docs[i]["description"]),
                                   "is_interactive": docs[i]["is_interactive"]})
                    
        return company_info_and_docs_processed
        
    def find_quarterly_reports_until_date(self, stock_symbol, date, cik=None):
        """ Gets the CIK number of the company and the accession number of the 10-Q forms going back
        to date. If cik is provided it will be used instead of stock_symbol.
            
        parameters
        --------
        stock_symbol: str
            stock symbol
        date: datetime.date
            Find the documents going back to this date.
        cik: str (optional)
            The CIK number. If provided it will be used instead of stock symbol.
        
        returns
        --------
        dict
            contains company info, including its CIK, and the accession number of the 10-Q forms
            and whether they have interactive data on sec.gov.
        
        """
        company_info_and_docs = \
            self._find_raw_quarterly_reports_until_date(stock_symbol, date, cik)
        
        company_info_and_docs_processed = \
            self._process_company_info_and_docs(company_info_and_docs)

        if cik is not None:
            assert int(company_info_and_docs_processed["info"]["cik"]) == int(cik)
        
        return company_info_and_docs_processed

    def _open_interactive_document_page(self, cik_num, acc_num):
        """It uses the company CIK number and the document accession number to open the interactive
        page of the document (if interactive data exists).
        
        parameters
        --------
        cik_num: str
            company CIK number
        acc_num: str
            financial document accession number
        
        """
        url = self.url_base + \
            "/cgi-bin/viewer?action=view&cik={}&accession_number={}&xbrl_type=v".\
            format(str(int(cik_num)), acc_num)

        self._open_url_with_retry(url)

    def _get_raw_quarterly_financial_statements_from_the_interactive_page(self):
        """Assuming the interactive quarterly report is open in the browser, it sifts through and
        finds the financial statements.
        
        returns
        --------
        dict
            financial statements in araw html tables
        """
        # financial statements button
        fs_element = self.driver.find_element_by_partial_link_text("Financial Statements")

        fs_element.click()
        
        time.sleep(5)
        
        # buttons opening below the financial statement button after it is clicked
        # fs_siblings[0] ---> financial statements button
        # fs_siblings[1] ---> buttons opening below the financial statements button
        fs_siblings = fs_element.find_elements_by_xpath("../*")
        assert len(fs_siblings) == 2
        
        # list of buttons pointing to various financial statements
        fs_list = fs_siblings[1].find_elements_by_xpath("*")

        # raw financial statements
        financial_statements = {}

        for i in range(len(fs_list)):
            try:
                fs_list[i].click()
            except ElementNotInteractableException:
                # The financial statement tab was closed, click to open it
                fs_element.click()
                time.sleep(2)
                fs_list[i].click()

            time.sleep(3)
            title = fs_list[i].find_element_by_tag_name("a").get_attribute("innerHTML")
            
            # financial statements data
            fs_data = fs_element.find_elements_by_xpath("../../../../../*")
            assert len(fs_data) == 2
            
            financial_statements[title] = fs_data[1].get_attribute('outerHTML')
        
        return financial_statements

    def get_raw_quarterly_financial_statements(self, cik_num, acc_num):
        """Open the interactive quarterly report page and extract financial statements.

        parameters
        --------
        cik_num: str
            company CIK number
        acc_num: str
            file accession number

        returns
        --------
        :dict
            financial statements
        """
        self._open_interactive_document_page(cik_num, acc_num)
        return self._get_raw_quarterly_financial_statements_from_the_interactive_page()