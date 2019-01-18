import locale

from django import template

register = template.Library()

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


@register.filter()
def currency(value):
    return locale.currency(value, grouping=True)


@register.simple_tag
def tran_type_desc(tran_type):
    if tran_type == 1:
        return 'Debit'
    elif tran_type == 2:
        return 'Credit'
    else:
        return 'Credit Card Payment'


@register.simple_tag
def month_name(month_id):
    switcher = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }
    return switcher.get(int(month_id), "Invalid Month!")
