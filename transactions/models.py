from django.contrib import admin
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    tran_dt = models.DateField()
    tran_desc = models.TextField()
    tran_type = models.SmallIntegerField(default=1, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True, blank=True)
    tran_amt = models.FloatField()

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
        return self.tran_desc + ' ' + str(self.tran_amt)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('tran_desc', 'tran_amt', 'month_yr', 'tran_type')
