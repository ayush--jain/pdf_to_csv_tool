"""
Canopy Python assignment
Ayush Jain
03/12/2020
"""

from poppler import load_from_file
import io
import re
import pandas as pd

def pdftotext(input_doc_path):
    '''
    Utility function to convert PDF file to text file using the Poppler library functions

    input_doc_path: Path for loading the input PDF file

    Returns:
        extracted text in string format
    '''
    #load PDF document and extract text using Poppler
    pdf_document = load_from_file(input_doc_path)
    pdf_text = pdf_document.create_page(0).text()

    return pdf_text

def create_row(lineitems):
    '''
    Utility function to create a single row based on the column names and
    extracted line items.

    lineitems: values and indices of all elements in row. Format: [value, index]

    Returns:
        dictionary with format {column_name: extracted_value}
    '''

    #add condition for initial line; only contains 4 elements
    if len(lineitems) == 4:
        debit, credit = "",""
        lineitems.insert(3, ["", ""])

    else:
        #check credit/debit value for 5th value in list
        #if difference between 5th and 6th value is less than 12 spaces, it is a credit amount
        if lineitems[-1][1] - lineitems[-2][1] < 6: credit, debit = lineitems[-2][0], ""
        else: debit, credit = lineitems[-2][0], ""

    #create one row based on the obtained values
    line_vals = {"Booking Date": lineitems[0][0],
                "Txn Date": lineitems[1][0], 
                "Booking Text": lineitems[2][0], 
                "Value Date": lineitems[3][0], 
                "Debit": debit, "Credit": credit, 
                "Balance": lineitems[-1][0]}

    return line_vals

def convert_to_csv(text):
    '''
    Utility function to identify required fields per row from the input text. 

    text: input text in string format, passed from the output of the Popppler extraction

    Returns:
        Pandas dataframe containing each row and column values. Format: [{"Booking Date": , ...},.....]
    '''
    
    #convert text to filestream
    buf = io.StringIO(text)
    text_lines= buf.readlines()

    prev_book_text = None
    output = []
    #iterate over all lines
    for line in text_lines:
        #remove leading and trailing spaces and split on multiple spaces (2 spaces)
        space_split_str = line.strip().split("  ")

        #if only one value found
        if len(space_split_str) == 1:
            #if value is not long enough or no detection of booking text yet
            if len(space_split_str[0]) < 5 or prev_book_text ==  None: continue
            #add line to previous booking text
            else: prev_book_text = prev_book_text + space_split_str[0] + "\n"

        else:
            #identify elements based on the spaces between them 
            lineitems = []
            for i in range(len(space_split_str)):
                if space_split_str[i] != "": lineitems.append((space_split_str[i], i))

            #set previous booking text to the value created so far if multi-line value is found
            if prev_book_text is not None and len(prev_book_text.split("\n")) > 1: 
                output[-1]["Booking Text"] = output[-1]["Booking Text"] + "\n" + prev_book_text

            prev_book_text = ""

            #ending criteria, 2 valued row indicating closing balance
            if len(lineitems) == 2:
                line_vals = {"Booking Text": lineitems[0][0],
                            "Balance": lineitems[1][0]}
                output.append(line_vals)
                break
                
            #add new row to output list
            else:
                line_vals = create_row(lineitems)
                output.append(line_vals)

    return pd.DataFrame(output[1:])

def main():

    #TEST PATH & OUTPUT PATH
    #can be read as sys arg, from config, API call, etc. Hardcoded here for simplicity
    TEST_PATH = "canopy_technical_test_input.pdf"
    OUTPUT_PATH = "output.csv"

    #get text output from PDF file
    pdf_text = pdftotext(TEST_PATH)

    #Call function to convert the PDF text to a dataframe
    df = convert_to_csv(pdf_text)

    #Export dataframe as a CSV file
    df.to_csv("output.csv", index=False)

if __name__ == "__main__":
	main()

    
