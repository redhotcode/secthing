#/usr/bin/env python3.4
from lxml import html, etree
import requests
import re
import json

class SECFiling:
    '''
        Simple class for parsing SEC Filings obtained from the internet into plain text paragraphs
        and splits the "financial" paragraphs (a.k.a. those paragraphs containing a dollar sign)
        into its own list.
        '''
    __slots__ = ['filing_url', 'paragraphs', 'financial_paragraphs']
    
    def __init__(self, filing_url, **kwargs):
        '''Creates a new SECFiling instance with the given SEC Filing URL as a string.'''
        self.filing_url = filing_url
    
    @property
    def page(self):
        '''The Response object containing the page obtained from the SEC filing URL.'''
        return requests.get(self.filing_url)
    
    @property
    def tree(self):
        '''Yields a tree of Elements from the HTML obtained from the page property.'''
        return html.document_fromstring(self.page.text)
    
    @property
    def paragraph_elements(self):
        '''Yields only those elements that contain text bodies.'''
        PARAGRAPH_SELECTOR = "//document/type/sequence/filename/description/text/div"
        return self.tree.xpath(PARAGRAPH_SELECTOR)
    
    def parse_paragraphs(self):
        '''
            Yields a dictionary with the text, paragraph start, and paragraph end position of each
            paragraph within the document. Strips text of invalid characters and ensures no
            tables are parsed. Also marks header texts (as denoted by their bold font weight) with a
            pound sign, making them valid Markdown headers.
            '''
        seq = self.paragraph_elements
        char_count, par_start, par_end = 0, 0, 0
        HEADING_SELECTOR = ".//font[contains(@style, 'font-weight:bold')]"
        TABLE_SELECTOR = ".//table"
        LINE_MIN_LEN = 5
        
        def filter_checkboxes(in_str):
            new_str = re.sub(r'[\xFD]+', r'X', in_str)
            new_str = re.sub(r'[\xA0]+', r'', new_str)
            return re.sub(r'[\xA8]', r'-', new_str)
        def filter_headers(in_str, element):
            return "# %s" % in_str if \
                len(element.xpath(HEADING_SELECTOR)) is not 0 else in_str
    
        for e in seq:
            if len(e.xpath(TABLE_SELECTOR)) is 0:
                text = filter_checkboxes(e.text_content())
                text = filter_headers(text, e)
                par_start, char_count, par_end = \
                    char_count, char_count + len(text), char_count
                if len(text) > LINE_MIN_LEN: yield {'text': text, 'start': par_start, 'end': par_end}

    def target_paragraphs(self):
        '''Generator yielding only the paragraphs containing a dollar sign ($). Yields dictionaries.'''
            for p in self.parse_paragraphs():
                if "$" in p['text']: yield p
                
    def save_plaintext(self, filename='document.txt'):
        '''Writes the plain text version of the SEC Filing to a text file.'''
        with open(filename, 'w') as f:
            for p in self.parse_paragraphs():
                f.write(p['text'] + "\n")
    
    def save_paragraphs(self, filename='paragraphs.txt'):
        '''Writes the paragraphs containing a dollars sign to a text file.'''
        with open(filename, 'w') as f:
            json.dump(list(self.target_paragraphs()), f)

def main():
    filing = SECFiling('http://www.sec.gov/Archives/edgar/data/9092/000000909214000004/bmi-20131231x10k.htm')
    filing.save_plaintext()
    filing.save_paragraphs()

if __name__ == "__main__":
    main()