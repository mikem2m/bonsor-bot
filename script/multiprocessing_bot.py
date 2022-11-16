"""Multiprocessing Volleyball Registration Automation (Webreg Burnaby) using Selenium

Functions
---------
multiprocess_bot(url, member_ids, family_pins)
"""

import os
from multiprocessing import Process
from dotenv import load_dotenv

from bot import RegistrationBot
from helper import generate_url


def multiprocessing_bot(url, ids, pins):
    """Register for volleyball spots simultaneously using the provided url and account information.

    Parameters
    ----------
    url (str)
        url for the volleyball registration
    ids (list of str)
        list of client number for webreg account
    pins (list of str)
        list of identification pin for webreg account

    Returns
    -------
    None
    """
    for member_id, family_pin in zip(ids, pins):
        process = Process(
            target=RegistrationBot.identification,
            args=(
                url,
                member_id,
                family_pin,
            ),
        )
        process.start()


if __name__ == '__main__':
    load_dotenv()
    member_ids = os.environ.get('MEMBER_IDS').split(' ')[:4]
    family_pins = os.environ.get('FAMILY_PINS').split(' ')[:4]
    multiprocessing_bot(generate_url(), member_ids, family_pins)
