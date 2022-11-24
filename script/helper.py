"""Constants module for RegistrationBot class.

Constants
---------
EDMONDS_TUESDAY_URL : str
    url for tuesday edmonds volleyball registration
EDMONDS_THURSDAY_URL : str
    url for thursday edmonds volleyball registration
BONSOR_TUESDAY_BEGINNER_URL : str
    url for tuesday bonsor volleyball beginner registration
BONSOR_TUESDAY_INTERMEDIATE_URL : str
    url for tuesday bonsor volleyball intermediate registration
BONSOR_FRIDAY_INTERMEDIATE_URL : str
    url for friday bonsor volleyball intermediate registration
BONSOR_REGISTRATION_TIME_HOUR : int
    time (hour) for volleyball registration
BONSOR_REGISTRATION_COST : float
    cost of one spot for volleyball registration
"""
from datetime import datetime

EDMONDS_TUESDAY_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8607"
)
EDMONDS_THURSDAY_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8614"
)
BONSOR_TUESDAY_BEGINNER_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8633"
)
BONSOR_TUESDAY_INTERMEDIATE_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8642"
)
BONSOR_FRIDAY_INTERMEDIATE_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8634"
)
BONSOR_REGISTRATION_TIME_HOUR = 9
BONSOR_REGISTRATION_COST = 5.25

def generate_url(type):
    """URL Generator based on the current weekday

    Parameters
    ----------
    None

    Returns
    -------
    url : str
        url for the volleyball registration
    """
    weekday = datetime.now().isoweekday()
    if weekday == 2:    # Tuesday
        if type == 'bonsor-inter':
            return BONSOR_TUESDAY_BEGINNER_URL
        if type == 'bonsor-beg':
            return BONSOR_TUESDAY_BEGINNER_URL
        return EDMONDS_TUESDAY_URL
    if weekday == 4:  # Thursday
        return EDMONDS_THURSDAY_URL
    if weekday == 5:  # Friday
        return BONSOR_FRIDAY_INTERMEDIATE_URL
    return None
