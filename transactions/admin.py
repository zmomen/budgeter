from django.contrib import admin

from .models import Transaction, TransactionAdmin

# Register your models here.
admin.site.register(Transaction, TransactionAdmin)
