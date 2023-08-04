import logging
import re
from datetime import datetime

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')


def parseAndGetFormattedTimeDifference(unformattedDate: str):
    formattedDate = unformattedDate.split(".")[0].replace("T", " ")

    try:
        startDatetime = datetime.strptime(formattedDate, "%Y-%m-%d %H:%M:%S")
        return getFormattedTimeDifference(datetime.now(), startDatetime)
    except ValueError:
        logger.error(
            f"ValueError during parsing of dates. Unformatted date: {unformattedDate}, formatted: {formattedDate}")
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


def strip_ansi_escape_codes(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def parse_tracebacks(logs):
    traceback_pattern = r"Traceback \(most recent call last\):(.*?)^\S*\s*(.+)\n"
    traceback_matches = re.findall(traceback_pattern, logs, re.DOTALL | re.MULTILINE)

    formatted_tracebacks = []
    for match in traceback_matches:
        exception_trace = match[0].strip()
        error_message = match[1].strip()
        formatted_traceback = f"{exception_trace}\n{error_message}"
        formatted_tracebacks.append(formatted_traceback)

    return formatted_tracebacks
