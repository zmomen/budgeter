from transactions.models import Transaction, Category


def bulk_insert_trans(data, file_type):

    # CAPITAL transactions
    if file_type == 'CAPITAL':
        for row in data:
            if len(Category.objects.filter(name__contains=row[4])) == 0:
                cat = Category.objects.create(name=row[4])
            else:
                cat = Category.objects.filter(name__contains=row[4])[0]

            deb = 0 if row[5] == '' else float(row[5])
            cred = 0 if row[6] == '' else float(row[6])
            Transaction.objects.create(tran_dt=row[0], tran_desc=row[3], category=cat,
                                       tran_amt=deb - cred, tran_type=1)
    # else PNC transactions
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
            # classify transaction categories.
            cat = Category.objects.get(id=12)
            Transaction.objects.create(tran_dt=row[0], tran_desc=row[1],category=cat,
                                       tran_amt=float(row[2]), tran_type=int(row[3]))
    return 'transactions inserted!'
