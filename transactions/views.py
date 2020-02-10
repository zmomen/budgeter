from django.contrib import messages
from django.db import models
from django.shortcuts import render, redirect

from transactions.models import Transaction, Category


def add_categories(request):
    return redirect('home:homepage')


def view_categories(request):
    if request.method == 'GET':
        return render(request, 'transactions/category.html')


def edit_category(request, action=None, id=None):
    if request.method == 'GET':
        if action == 'remove' and id:
            cat = Category.objects.get(id=id)
            cat.delete()
            return redirect('transactions:view-categories')
        elif action == 'add':
            c = Category(name=request.GET.get('new_cat'))
            c.save()
            # print(c)
            return redirect('transactions:view-categories')


def search(request):
    if request.method == 'GET':
        searchQry = request.GET.get('txtSearch')
        from_date = request.GET.get('from_date') if request.GET.get('from_date') != '' else '1970-01-01'
        to_date = request.GET.get('to_date') if request.GET.get('to_date') != '' else '2099-01-01'
        if len(searchQry.replace(' ', '')) == 0 and from_date == '1970-01-01' and to_date == '2099-01-01':
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

    args = {'query_results': found, 'searchQry': [searchQry, from_date, to_date]}
    return render(request, 'home/search_results.html', args)


def edit_transaction(request, id=None):
    if request.method == "POST":
        # print(request.POST)
        for key in request.POST:
            if 'tran_id' in key:
                tran_id = request.POST[key]  # value of tran_id
                new_cat = Category.objects.get(name=request.POST['cat_id' + tran_id])
                new_desc = request.POST['tran_desc' + tran_id]
                tran = Transaction.objects.filter(id=tran_id).update(category=new_cat, tran_desc=new_desc)

        messages.add_message(request, messages.INFO, 'Transaction updated!')
    elif request.method == "GET":
        tran = Transaction.objects.get(id=id)
        tran.delete()
        messages.add_message(request, messages.INFO, 'deleted!')
    return redirect('home:homepage')


def bulk_insert_trans(request, data, file_type):
    if request.method == "POST":
        total_rows = 0
        # CAPITAL transactions
        if file_type == 'CAPITAL':
            for row in data:
                total_rows += 1
                if len(Category.objects.filter(name__contains=row[4])) == 0:
                    cat = Category.objects.create(name=row[4])
                else:
                    cat = Category.objects.filter(name__contains=row[4])[0]

                deb = 0 if row[5] == '' else float(row[5])
                cred = 0 if row[6] == '' else float(row[6])
                Transaction.objects.create(tran_dt=row[0], tran_desc=row[3], category=cat,
                                           tran_amt=deb - cred, tran_type=1)
        # else PNC transaction
        else:
            # remove characters and prep for float conversion.
            data = [[item.replace('$', '').replace(',', '').replace('  ', ' ')
                         .replace('/', '').rstrip() for item in lst] for lst in data]
            for row in data:
                if 'CAPITAL' in ' '.join(row):
                    data.remove(row)

            for i in range(len(data)):
                # remove balance and convert the date
                val = data[i][0]
                val = val[4:] + '-' + val[:2] + '-' + val[2:4]
                data[i][0] = str(val)
                data[i] = data[i][:-1]
                if data[i][-2] == '':
                    del data[i][-2]
                    data[i].append(2)  # 'Credit'
                else:
                    del data[i][-1]
                    data[i].append(1)  # 'Debit'

            for row in data:
                total_rows += 1
                # classify transaction categories.
                cat = Category.objects.get(id=determine_category_id(row[1]))
                Transaction.objects.create(tran_dt=row[0], tran_desc="PNC-" + row[1], category=cat,
                                           tran_amt=float(row[2]), tran_type=int(row[3]))

        # pct = 'Percentage: %8.2f%%' % bc.get_accuracy()
        messages.add_message(request, messages.ERROR, str(total_rows) + ' transactions inserted!')
    return redirect('home:homepage')


def determine_category_id(tran_description):
    upper_desc = str.upper(tran_description)

    for income in ["CASHOUT", "REIMBURSEMENT", "PAYROLL", "INVESTMENT", "INTEREST"]:
        if income in upper_desc:
            return 13
    if "VENMO" in upper_desc:
        return 15
    if "ATM WITHDRAWAL" in upper_desc:
        return 5

    return 12
