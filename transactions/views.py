from django.contrib import messages
from django.db import models
from django.shortcuts import render, redirect

from transactions.models import Transaction, Category


# Create your views here.
def reports(request, year=None, month=None, cat_id=None):
    # by month and year
    if year and month:
        month_id_spend = Transaction.objects.values('tran_dt', 'tran_desc', 'category__name') \
            .exclude(category__name__in=['Deposit', 'Credit Card']) \
            .annotate(year=models.functions.ExtractYear('tran_dt')) \
            .annotate(month=models.functions.ExtractMonth('tran_dt')) \
            .annotate(totals=models.Sum('tran_amt')) \
            .filter(year=year, month=month) \
            .values('tran_dt', 'tran_desc', 'category__name', 'totals') \
            .order_by('-tran_dt', 'category__name', '-totals')

        args = {'month_id_spend': month_id_spend, 'report_type': 'by month', 'monthYear': [month, year]}
        return render(request, 'transactions/report_by_id.html', args)
    # else by category_id
    elif cat_id:
        cat_id_spend = Transaction.objects.values('tran_dt', 'tran_type', 'tran_desc', 'category__name',
                                                  'category__id') \
            .annotate(totals=models.Sum('tran_amt')) \
            .filter(category__id=cat_id) \
            .values('tran_dt', 'tran_type', 'tran_desc', 'category__name', 'totals') \
            .order_by('-tran_dt', 'category__name', '-totals')
        category_name = Category.objects.get(id=cat_id).name
        args = {'cat_id_spend': cat_id_spend, 'report_type': 'by category', 'category_name': category_name}
        return render(request, 'transactions/report_by_id.html', args)
    # else main page.
    else:
        cat_spend = Transaction.objects.values('category__name', 'category__id') \
            .annotate(totals=models.Sum('tran_amt')) \
            .order_by('-totals', 'category__name')

        month_spend = Transaction.objects.annotate(year=models.functions.ExtractYear('tran_dt')) \
            .exclude(category__name__in=['Deposit', 'Credit Card']) \
            .annotate(month=models.functions.ExtractMonth('tran_dt')).values('year', 'month') \
            .annotate(totals=models.Sum('tran_amt')).order_by('-year', '-month', '-totals')

        deposits = Transaction.objects.filter(tran_type=2) \
            .annotate(year=models.functions.ExtractYear('tran_dt')) \
            .annotate(month=models.functions.ExtractMonth('tran_dt')).values('year', 'month') \
            .annotate(totals=models.Sum('tran_amt')).order_by('-year', '-month', '-totals')

        args = {'cat_spend': cat_spend, 'month_spend': month_spend, 'deposits': deposits}

        return render(request, 'transactions/reports.html', args)


def add_categories(request):
    return redirect('home:homepage')


def view_categories(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        args = {'categories': categories}

        return render(request, 'transactions/category.html', args)


def edit_category(request, action=None, id=None):
    if request.method == 'GET':
        if action == 'remove' and id:
            cat = Category.objects.get(id=id)
            cat.delete()
            return redirect('transactions:view-categories')
        elif action == 'add':
            c = Category(name=request.GET.get('new_cat'))
            c.save()
            print(c)
            return redirect('transactions:view-categories')


def search(request):
    if request.method == 'GET':
        searchQry = request.GET.get('txtSearch')
        from_date = request.GET.get('from_date') if request.GET.get('from_date') != '' else '1970-01-01'
        to_date = request.GET.get('to_date') if request.GET.get('to_date') != '' else '2099-01-01'
        if searchQry == '' and from_date == '1970-01-01' and to_date == '2099-01-01':
            messages.add_message(request, messages.ERROR, 'Error: No search value provided!')
            return redirect('home:homepage')

        else:

            found = Transaction.objects.filter(models.Q(tran_desc__contains=searchQry) | \
                                               models.Q(category__name__contains=searchQry)).order_by('-tran_dt')
            if searchQry.isnumeric():
                found = found | Transaction.objects.filter(
                    tran_amt__range=(float(searchQry) - 10, float(searchQry) + 10)).order_by('-tran_dt')

            if searchQry.lower() == 'debit':
                found = found | Transaction.objects.filter(tran_type=1).order_by('-tran_dt')
            elif searchQry.lower() == 'credit':
                found = found | Transaction.objects.filter(tran_type=2).order_by('-tran_dt')
            elif searchQry.lower() == 'payment':
                found = found | Transaction.objects.filter(tran_type=3).order_by('-tran_dt')

            # filter by dates
            found = found & Transaction.objects.filter(tran_dt__range=(from_date, to_date)).order_by('-tran_dt')
    categories = Category.objects.all()

    args = {'query_results': found, 'searchQry': [searchQry, from_date, to_date], 'categories': categories}
    return render(request, 'home/search_results.html', args)


def edit_transaction(request, id=None):
    if request.method == "POST":
        print(request.POST)
        for key in request.POST:
            if 'tran_id' in key:
                tran_id = request.POST[key]  # value of tran_id
                new_cat = Category.objects.get(name=request.POST['cat_id' + tran_id])
                new_desc = request.POST['tran_desc' + tran_id]
                tran = Transaction.objects.filter(id=tran_id).update(category=new_cat, tran_desc=new_desc)
        messages.add_message(request, messages.INFO, 'Transaction ' + ' updated!')
    elif request.method == "GET":
        tran = Transaction.objects.get(id=id)
        tran.delete()
        messages.add_message(request, messages.INFO, tran + 'deleted!')
    return redirect('home:homepage')
