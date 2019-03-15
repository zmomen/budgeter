from django.shortcuts import render

from transactions.models import Transaction, Category


# Create your views here.
def reports(request, tran_type=None, year=None, month=None, cat_id=None):
    # by month and year
    if year and month:
        month_id_details = Transaction.objects.get_month_details(year=year, month=month, tran_type=tran_type)
        args = {'month_id_details': month_id_details, 'report_type': 'by month', 'monthYear': [month, year]}

        return render(request, 'reports/report_by_id.html', args)

    # else by category_id
    elif cat_id:
        cat_id_spend = Transaction.objects.get_by_cat_id(cat_id=cat_id)
        category_name = Category.objects.get(id=cat_id).name

        args = {'cat_id_spend': cat_id_spend, 'report_type': 'by category', 'category_name': category_name}
        return render(request, 'reports/report_by_id.html', args)
    # else main page.
    else:
        cat_spend = Transaction.objects.get_cat_spend()
        month_spend = Transaction.objects.display_by_month_year()
        deposits = Transaction.objects.get_deposit_trans()

        args = {'cat_spend': cat_spend, 'month_spend': month_spend, 'deposits': deposits}
        return render(request, 'reports/reports.html', args)

