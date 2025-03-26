from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    TRANSACTION_TYPES = [
        (INCOME, "Доход"),
        (EXPENSE, "Расход"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=50)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.type}"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.FloatField()
    saved_amount = models.FloatField(default=0)
    deadline = models.DateTimeField(default=timezone.now)
    saving_percentage = models.FloatField(default=10)
    is_active = models.BooleanField(default=True)

    def progress(self):
        return min(int((self.saved_amount / self.target_amount) * 100), 100)

    def remaining_amount(self):
        return max(self.target_amount - self.saved_amount, 0)

    def __str__(self):
        return f"{self.user.username} - {self.name}"