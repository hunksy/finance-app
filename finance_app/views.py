from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login  
from .forms import RegisterForm, TransactionForm, GoalForm
from django.contrib.auth.decorators import login_required
from .models import Transaction, Goal
from django.db.models import Sum, F
from django.contrib import messages
import json
from datetime import datetime, timedelta
import csv
import io
import chardet

def register(request):  
    if request.method == "POST":  
        form = RegisterForm(request.POST)  
        if form.is_valid():  
            user = form.save()  
            login(request, user)
            return redirect("profile")  
    else:  
        form = RegisterForm()  
    return render(request, "register.html", {"form": form})

@login_required
def profile(request):
    return render(request, "profile.html")

def home(request):
    return redirect("profile")

def update_goal(user, income_amount):
    active_goals = Goal.objects.filter(user=user, is_active=True)

    for goal in active_goals:
        saved_amount = (goal.saving_percentage / 100) * income_amount
        Goal.objects.filter(id=goal.id).update(saved_amount=F("saved_amount") + saved_amount)

@login_required
def transactions_view(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            if transaction.type == "income":
                active_goals = Goal.objects.filter(user=request.user, is_active=True)

                for goal in active_goals:
                    saved_amount = round((goal.saving_percentage / 100) * transaction.amount)
                    Goal.objects.filter(id=goal.id).update(saved_amount=F("saved_amount") + saved_amount)

                    goal.refresh_from_db()
                    if goal.progress() >= 50:
                        messages.info(request, f"Вы достигли {int(goal.progress())}% вашей цели: {goal.name}!")

            return redirect("transactions")

    else:
        form = TransactionForm()

    transactions = Transaction.objects.filter(user=request.user)
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    category = request.GET.get("category")
    transaction_type = request.GET.get("type")

    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    if category:
        transactions = transactions.filter(category=category)
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)

    return render(request, "transactions.html", {
        "form": form,
        "transactions": transactions,
    })

@login_required
def goals_page(request):
    goals = Goal.objects.filter(user=request.user)

    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("goals_page")
    else:
        form = GoalForm()

    return render(request, "goals_page.html", {"goals": goals, "form": form})

@login_required
def toggle_active(request, goal_id):
    goal = Goal.objects.get(id=goal_id, user=request.user)
    goal.is_active = not(goal.is_active)
    goal.save()
    return redirect("goals_page")

@login_required
def analytics(request):
    transactions = Transaction.objects.filter(user=request.user)

    expenses = transactions.filter(type="expense").values("category").annotate(total=Sum("amount"))
    incomes = transactions.filter(type="income").values("category").annotate(total=Sum("amount"))

    expense_labels = [item["category"] for item in expenses]
    expense_values = [item["total"] for item in expenses]

    income_labels = [item["category"] for item in incomes]
    income_values = [item["total"] for item in incomes]

    if expenses:
        max_expense = max(expenses, key=lambda x: x["total"])
        recommendation = f"Вы тратите слишком много на {max_expense['category']}. Попробуйте сократить расходы."
    else:
        recommendation = "Нет данных о расходах."

    return render(request, "analytics.html", {
        "expense_labels": json.dumps(expense_labels),
        "expense_values": json.dumps(expense_values),
        "income_labels": json.dumps(income_labels),
        "income_values": json.dumps(income_values),
        "recommendation": recommendation,
    })

def reports_view(request):
    period = request.GET.get("period", "month")

    transactions = Transaction.objects.filter(user=request.user)

    if request.method == "POST" and "csv_file" in request.FILES:
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            return render(request, "reports.html", {"error": "Неверный формат файла", "transactions": transactions, "period": period})

        raw_data = csv_file.read()
        detected_encoding = chardet.detect(raw_data)["encoding"]

        decoded_file = io.StringIO(raw_data.decode(detected_encoding, errors="replace"))

        reader = csv.reader(decoded_file, delimiter=",")
        next(reader)

        for row in reader:
            try:
                date = datetime.strptime(row[0], "%d.%m.%Y")
                type = "income" if row[1].strip().lower() == "доход" else "expense"
                category = row[2].strip()
                amount = float(row[3].replace(",", "."))

                Transaction.objects.create(user=request.user, date=date, type=type, category=category, amount=amount)
            except Exception as e:
                print(f"Ошибка при обработке строки: {row} - {e}")

        return redirect("reports")

    return render(request, "reports.html", {"transactions": transactions, "period": period})

@login_required
def export_csv(request):
    period = request.GET.get("period", "month")
    user_transactions = Transaction.objects.filter(user=request.user)

    today = datetime.today()
    if period == "month":
        start_date = today.replace(day=1)
    elif period == "quarter":
        start_date = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today - timedelta(days=30)

    transactions = user_transactions.filter(date__gte=start_date)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="report_{period}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Дата", "Тип", "Категория", "Сумма"])
    for transaction in transactions:
        writer.writerow([transaction.date.strftime("%d.%m.%Y"), transaction.get_type_display(), transaction.category, transaction.amount])

    return response
