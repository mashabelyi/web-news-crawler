import re 

def next_day(date):
    """
    Return date tuple for next day in calendar year
    
    Args:
    date (tuple): ( (int) yr, (int) month, (int) day)
    """

    yr = date[0]
    m = date[1]
    d = date[2]

    d += 1
    if d > 31:
        m += 1
        d = 1
    if m > 12:
        yr += 1
        m == 1

    return (yr, m, d)

def int_to_date(date_int):
    """
    Returns date tuple (yr, month, day)

    Args:
    date_int (int): integer timestamp representation. e.g. 20180803 (Aug 03, 2018)
    """
    date = str(date_int)
    yr = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    return (int(yr), int(mm), int(dd))


def date_to_path(date):
    """
    Converts date tuple to url path
    e.g. yyyy/mm/dd

    Args:
    date (tuple): ( (int) yr, (int) month, (int) day)

    Example:
    input: (2018, 8, 3)
    return: '2018/08/03'
    """
    return "{}/{:02d}/{:02d}".format(date[0], date[1], date[2])

def info_from_url(url):
    """
    Parse out relevant info from url

    Return:
    topic (String) if applicable
    date (tuple(string)) e.g. (2018, 08, 03) 
    """
    m = re.search('.+\.com\/(.+)\/(\d{4}\/\d{2}\/\d{2})\/.+', url)
    topic = m.group(1)
    date = tuple(m.group(2).split("/"))

    return topic, date




