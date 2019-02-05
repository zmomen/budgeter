from django.contrib import admin
from django.db import models
from django.db.models import functions, Sum
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.name


class TransactionsManager(models.Manager):

    def get_month_details(self, year, month):
        return self.values('tran_dt', 'tran_desc', 'category__name') \
            .exclude(category__name__in=['Deposit', 'Credit Card']) \
            .annotate(year=functions.ExtractYear('tran_dt')) \
            .annotate(month=functions.ExtractMonth('tran_dt')) \
            .annotate(totals=Sum('tran_amt')) \
            .filter(year=year, month=month) \
            .values('tran_dt', 'tran_desc', 'category__name', 'totals') \
            .order_by('-tran_dt', 'category__name', '-totals')

    def get_by_cat_id(self, cat_id):
        return self.values('tran_dt', 'tran_type', 'tran_desc', 'category__name','category__id') \
            .annotate(totals=Sum('tran_amt')) \
            .filter(category__id=cat_id) \
            .values('tran_dt', 'tran_type', 'tran_desc', 'category__name', 'totals') \
            .order_by('-tran_dt', 'category__name', '-totals')

    def get_cat_spend(self):
        return self.values('category__name', 'category__id') \
            .annotate(totals=Sum('tran_amt')) \
            .order_by('-totals', 'category__name')

    def display_by_month_year(self):
        return self.annotate(year=functions.ExtractYear('tran_dt')) \
            .exclude(category__name__in=['Deposit', 'Credit Card']) \
            .annotate(month=functions.ExtractMonth('tran_dt')).values('year', 'month') \
            .annotate(totals=Sum('tran_amt')).order_by('-year', '-month', '-totals')

    def get_deposit_trans(self):
        return self.filter(tran_type=2) \
            .annotate(year=functions.ExtractYear('tran_dt')) \
            .annotate(month=functions.ExtractMonth('tran_dt')).values('year', 'month') \
            .annotate(totals=Sum('tran_amt')).order_by('-year', '-month', '-totals')


class Transaction(models.Model):
    tran_dt = models.DateField()
    tran_desc = models.TextField()
    tran_type = models.SmallIntegerField(default=1, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True, blank=True)
    tran_amt = models.FloatField()
    objects = TransactionsManager()

    def month_yr(self):
        return self.tran_dt.strftime('%b %Y')

    def tran_type_desc(self):
        if self.tran_type == 1:
            return 'Debit'
        elif self.tran_type == 2:
            return 'Credit'
        elif self.tran_type == 3:
            return 'Credit Card Payment'

    def __str__(self):
        return self.tran_desc


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('tran_desc', 'tran_amt', 'month_yr', 'tran_type')
