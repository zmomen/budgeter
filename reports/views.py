from django.db.models import functions, Sum
from django.shortcuts import render

from transactions.models import Transaction, Category


# Create your views here.
def reports(request, year=None, month=None, cat_id=None):
    # by month and year
    if year and month:
        month_id_spend = Transaction.objects.values('tran_dt', 'tran_desc', 'category__name') \
            .exclude(category__name__in=['Deposit', 'Credit Card']) \
            .annotate(year=functions.ExtractYear('tran_dt')) \
            .annotate(month=functions.ExtractMonth('tran_dt')) \
            .annotate(totals=Sum('tran_amt')) \
            .filter(year=year, month=month) \
            .values('tran_dt', 'tran_desc', 'category__name', 'totals') \
            .order_by('-tran_dt', 'category__name', '-totals')

        args = {'month_id_spend': month_id_spend, 'report_type': 'by month', 'monthYear': [month, year]}
        return render(request, 'transactions/report_by_id.html', args)
    # else by category_id
    elif cat_id:
        cat_id_spend = Transaction.objects.values('tran_dt', 'tran_type', 'tran_desc', 'category__name',
                                                  'category__id') \
            .annotate(totals=Sum('tran_amt')) \
            .filter(category__id=cat_id) \
            .values('tran_dt', 'tran_type', 'tran_desc', 'category__name', 'totals') \
            .order_by('-tran_dt', 'category__name', '-totals')
        category_name = Category.objects.get(id=cat_id).name
        args = {'cat_id_spend': cat_id_spend, 'report_type': 'by category', 'category_name': category_name}
        return render(request, 'transactions/report_by_id.html', args)
    # else main page.
    else:
        cat_spend = Transaction.objects.values('category__name', 'category__id') \
            .annotate(totals=Sum('tran_amt')) \
            .order_by('-totals', 'category__name')

        month_spend = Transaction.objects.annotate(year=functions.ExtractYear('tran_dt')) \
            .exclude(category__name__in=['Deposit', 'Credit Card']) \
            .annotate(month=functions.ExtractMonth('tran_dt')).values('year', 'month') \
            .annotate(totals=Sum('tran_amt')).order_by('-year', '-month', '-totals')

        deposits = Transaction.objects.filter(tran_type=2) \
            .annotate(year=functions.ExtractYear('tran_dt')) \
            .annotate(month=functions.ExtractMonth('tran_dt')).values('year', 'month') \
            .annotate(totals=Sum('tran_amt')).order_by('-year', '-month', '-totals')

        args = {'cat_spend': cat_spend, 'month_spend': month_spend, 'deposits': deposits}

        return render(request, 'transactions/reports.html', args)
