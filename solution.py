#!/usr/bin/env python3.4

import html2text
import json
import urllib.request

url = 'http://www.sec.gov/Archives/edgar/data/9092/000000909214000004/bmi-20131231x10k.htm'

with urllib.request.urlopen(url) as response:
    html = response.read()
    text = html2text.html2text(html.decode())
    
    doc = open("document.txt", "w") # Open a file to write the plain text to
    doc.write(text)                 # and dump the converted text into it
    
    in_paragraph = False   # We are by default not "inside" of a paragraph yet
    newline_found = False  # Two newlines denote a new paragraph
    sentinel_found = False # Whether or not the $ has been encountered yet
    found = []             # This will hold all of the paragraphs with a $ in the text
    start_idx = -1         # Set index to -1 to indicate we aren't inside a paragraph yet
    end_idx = -1           # Do the same to indicate that we haven't reached the end either
    para_text = ""         # Holds the text of each paragraph
    
    # Go through the plain text character by character, adding each
    # character in a paragraph to a string, and if the setinel character
    # is encountered, we add the paragraph to our list of paragraphs,
    # noting its starting and ending index.
    for i in range(0, len(text)):
        if not in_paragraph:
            if text[i].isalnum():
                in_paragraph = True
                start_idx = i
                para_text += text[i]
        elif text[i] == '$':
            sentinel_found = True
            para_text += text[i]
        elif text[i] == '\n':
            if newline_found:
                end_idx = i - 1
                newline_found = False
                if sentinel_found:
                    found = found + [{'start': start_idx, 'end': end_idx, 'text': para_text}]
                sentinel_found = False
                start_idx = -1
                in_paragraph = False
                para_text = ""
            else:
                newline_found = True
                para_text += text[i]
        else:
            para_text += text[i]
    with open('paragraphs.txt', 'w') as fp:
        json.dump(found, fp)