import logging
from datetime import datetime

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')


def parseAndGetFormattedTimeDifference(unformattedDate: str):
    formattedDate = unformattedDate.split(".")[0].replace("T", " ")

    try:
        startDatetime = datetime.strptime(formattedDate, "%Y-%m-%d %H:%M:%S")
        return getFormattedTimeDifference(datetime.now(), startDatetime)
    except ValueError:
        logger.error(f"ValueError during parsing of dates. Unformatted date: {unformattedDate}, formatted: {formattedDate}")
        raise ValueError


def getFormattedTimeDifference(firstDate: datetime, secondDate: datetime):
    time_difference = firstDate - secondDate

    # Extract the number of days, hours, and minutes from the time difference
    days = abs(time_difference.days)
    hours = time_difference.seconds // 3600
    minutes = (time_difference.seconds // 60) % 60

    # lol a little long perhaps
    return f"{formatAmount('day', days)} and {formatAmount('hour', hours)}" if days > 0 \
        else f"{formatAmount('hour', hours)} and {formatAmount('minute', minutes)}"


def formatAmount(base: str, amount: int):
    return f"{amount} {base}{'s' if amount != 1 else ''}"
