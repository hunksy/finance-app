from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Transaction, Goal


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "category", "amount", "date"]
        labels = {
            "type": "Тип операции",
            "category": "Категория",
            "amount": "Сумма",
            "date": "Дата",
        }
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Сумма должна быть положительной.")

        return amount


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["name", "target_amount", "deadline", "saving_percentage"]
        labels = {
            "name": "Название цели",
            "target_amount": "Целевая сумма",
            "deadline": "Дедлайн",
            "saving_percentage": "Процент от дохода",
            "is_active": "Цель активна"
        }
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
