

class AccountsNotFoundError(Exception):
    '''
    Raised when no accounts are found through companies house API
    Raised in get_pdf.py
    '''
    pass

class NoPhraseInPDFError(Exception):
    '''
    Raised when there are no images of the pages of the filtered PDF
    Occurs when there are no wanted phrases in the PDF
    '''
    pass

class FailedToExtractDataError(Exception):
    '''
    Raised when there is not enough data found in the filtered PDF image to extract the data
    For example, when there's only one column found
    '''
    pass