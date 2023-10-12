class AgendaItemClassificationError(Exception):
    """
    Raised when attemptimg an invaild method on an Agenda Item.

    i.e.: Attempting to change the status of an Internally Requested Feature Request to an invaild status such as FYI or Open
    """

    pass


class DuplicateUsernameError(Exception):
    """
    Raised when attemptimg to create a user with a duplicated username.
    """

    pass
