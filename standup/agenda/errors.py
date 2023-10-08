class AgendaItemClassificationError(Exception):
    """
    Raised when attemptimg an invaild method on an Agenda Item.

    i.e.: Attempting to change the status of an Internally Requested Feature Request to an invaild status such as FYI or Open

    Args:
        Exception (_type_): _description_
    """

    pass
