# Module for naming Labelling all data from business_metrics and product_metrics into labelled data
from scipy import stats


def main():
    """write the script to label all the data from the sql tables"""
    return NotImplementedError

def hypothesis_testing(table, column, values):
    """Takes a particular value from a table and column as the population then does the 2 tailed test to determine
    if the particular value of a row is less than more than or expected and returns the label from the list values that
    represents it"""
    return NotImplementedError

def label():
    """genericly label all the random variables that can be done using simple hypothesis testing"""
    return NotImplementedError

# advanced labelling functions
def label_sales():
    """label sales"""
    return NotImplementedError

def label_competions():
    """label competition"""
    return NotImplementedError

def label_product_popularity():
    """label product_popularity"""
    return NotImplementedError

def label_pricing():
    """label pricing"""
    return NotImplementedError

def label_stocking():
    """label stocking"""
    return NotImplementedError

def label_season():
    """label season"""
    return NotImplementedError

def save_labelled_row():
    """after labelling a month save it on the labelled table"""
    return NotImplementedError

if __name__ == "__main__":
    main()