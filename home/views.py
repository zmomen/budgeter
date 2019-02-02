import codecs
import csv

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from transactions.helpers import bulk_insert_trans
from transactions.models import Transaction, Category


# Create your views here.
class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get(self, request, **kwargs):
        try:
            page = request.GET.get('page', 1)
            trans_list = Transaction.objects.order_by('-tran_dt')
            paginator = Paginator(trans_list, 10)
            trans = paginator.page(page)
            total_records = Transaction.objects.all().count()
            categories = Category.objects.all()

            args = {'upload_results': trans, 'total_records': total_records, 'categories': categories}

        except PageNotAnInteger:
            trans = paginator.page(1)
        except EmptyPage:
            trans = paginator.page(paginator.num_pages)
            return render(request, 'home/error_404.html')

        return render(request, 'home/index.html', args)


# https://www.pythoncircle.com/post/30/how-to-upload-and-process-the-csv-file-in-django/
def upload_csv(request):
    #    try:
    file = request.FILES["csv_file"]
    if not file.name.endswith('.csv'):
        print('ERROR WONG FILE!')
        messages.add_message(request, messages.ERROR, 'ERROR: WONG FILE!')
        return render(request, 'home/index.html')

    reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
    next(reader, None)

    data = []
    for line in reader:
        data.append(line)

    file_type = request.POST.get('file_type', '')
    bulk_insert_trans(data, file_type)
    print('inserting transactions...')

    # pct = 'Percentage: %8.2f%%' % bc.get_accuracy()
    # messages.add_message(request, messages.ERROR, pct)
    return redirect('home:homepage')
