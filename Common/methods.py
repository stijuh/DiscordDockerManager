from datetime import datetime


def parseAndGetFormattedTimeDifference(unformattedDate: str):
    formattedDate = unformattedDate[:-9].replace("T", " ")
    startDatetime = datetime.strptime(formattedDate, "%Y-%m-%d %H:%M:%S")

    return getFormattedTimeDifference(datetime.now(), startDatetime)


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
