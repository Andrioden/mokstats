import calendar


def month_name(month_number: int) -> str:
    return calendar.month_name[month_number]


def month_number_padded(month_number: int) -> str:
    if month_number < 10:
        return "0%s" % month_number
    else:
        return str(month_number)
