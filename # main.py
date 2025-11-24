# main.py
import csv
import os
import datetime
import sys
OUT_SUMMARY = "summary.txt" 
DATA_FILE = "finance_data.csv"
ANNUAL_RETURN = 0.10  
def tax_new_regime(annual_income):
    tax = 0.0
    if annual_income <= 300000:
        return 0.0
    slab = max(0, min(annual_income, 700000) - 300000)
    tax += slab * 0.05
    slab = max(0, min(annual_income, 1000000) - 700000)
    tax += slab * 0.10
    slab = max(0, min(annual_income, 1200000) - 1000000)
    tax += slab * 0.15
    slab = max(0, min(annual_income, 1500000) - 1200000)
    tax += slab * 0.20
    slab = max(0, annual_income - 1500000)
    tax += slab * 0.30
    return round(tax, 2)
def monthly_to_annual(m): return m * 12.0
def annual_to_monthly(a): return a / 12.0
def future_value_monthly_saved(monthly_contrib, years, annual_rate=ANNUAL_RETURN):
    if monthly_contrib <= 0:
        return 0.0
    months = int(years * 12)
    monthly_rate = annual_rate / 12.0
    if monthly_rate == 0:
        return round(monthly_contrib * months, 2)
    fv = monthly_contrib * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    return round(fv, 2)
def suggest_investment_mix(monthly_surplus):
    if monthly_surplus <= 0:
        return "No surplus to invest. Prioritise reducing expenses and building an emergency fund."
    if monthly_surplus < 5000:
        return "Emergency fund (3-6 months) → then small RD / liquid fund."
    if monthly_surplus < 20000:
        return "60% SIP (equity), 20% RD/FD (debt), 10% Gold, 10% Emergency."
    return "50% SIP (equity), 20% NPS/retirement, 15% FD/RD (debt), 10% Gold, 5% Liquid."
def affordability_prediction(target_price, monthly_surplus, years):
    fv = future_value_monthly_saved(monthly_surplus, years)
    can_afford = fv >= target_price
    return fv, can_afford
def format_currency(x): return f"₹{x:,.2f}"
def append_session_row(row):
    header = ["timestamp", "user_type", "monthly_income", "monthly_expenses",
              "total_monthly_emi", "monthly_surplus", "net_monthly_income_after_tax"]
    exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(header)
        w.writerow(row)
def run_student_flow():
    print("\n-- Student Mode (minimal) --")
    while True:
        try:
            monthly_income = float(input("Monthly allowance / income (₹): ").strip() or 0)
            break
        except ValueError:
            print("Enter a valid number (example: 5000).")
    while True:
        try:
            monthly_expenses = float(input("Monthly expenses (₹): ").strip() or 0)
            break
        except ValueError:
            print("Enter a valid number.")
    total_emi = 0.0  
    gross_annual = monthly_to_annual(monthly_income)
    tax = tax_new_regime(gross_annual)
    net_annual = gross_annual - tax
    net_monthly = annual_to_monthly(net_annual)
    monthly_surplus = net_monthly - monthly_expenses - total_emi
    return {
        "user_type": "Student",
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "total_monthly_emi": total_emi,
        "tax_annual": tax,
        "net_monthly_income_after_tax": round(net_monthly, 2),
        "monthly_surplus": round(monthly_surplus, 2)
    }
def run_worker_flow():
    print("\n-- Working Professional Mode (minimal) --")
    while True:
        try:
            monthly_salary = float(input("Monthly gross salary (₹): ").strip() or 0)
            break
        except ValueError:
            print("Enter a valid number.")
    while True:
        try:
            monthly_expenses = float(input("Monthly expenses (basic) (₹): ").strip() or 0)
            break
        except ValueError:
            print("Enter a valid number.")
    while True:
        try:
            total_emi = float(input("Total monthly EMI (combined) (₹) — enter 0 if none: ").strip() or 0)
            break
        except ValueError:
            print("Enter a valid number.")
    gross_annual = monthly_to_annual(monthly_salary)
    tax = tax_new_regime(gross_annual)
    net_annual = gross_annual - tax
    net_monthly = annual_to_monthly(net_annual)
    monthly_surplus = net_monthly - monthly_expenses - total_emi
    return {
        "user_type": "Working",
        "monthly_income": monthly_salary,
        "monthly_expenses": monthly_expenses,
        "total_monthly_emi": total_emi,
        "tax_annual": tax,
        "net_monthly_income_after_tax": round(net_monthly, 2),
        "monthly_surplus": round(monthly_surplus, 2)
    }
def build_summary(data):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    surplus = data["monthly_surplus"]
    fv1 = future_value_monthly_saved(max(0, surplus), 1)
    fv5 = future_value_monthly_saved(max(0, surplus), 5)
    fv10 = future_value_monthly_saved(max(0, surplus), 10)
    invest = suggest_investment_mix(surplus)
    car_price = 1_000_000
    house_dp = 500_000
    child_fund = 1_500_000
    carfv, carok = affordability_prediction(car_price, max(0, surplus), 5)
    housefv, houseok = affordability_prediction(house_dp, max(0, surplus), 5)
    childfv, childok = affordability_prediction(child_fund, max(0, surplus), 10)
    lines = [
        "SMART PERSONAL FINANCE PLANNER — SUMMARY",
        f"Generated: {now}",
        f"User type: {data['user_type']}",
        "----",
        f"Monthly Income (gross): {format_currency(data['monthly_income'])}",
        f"Monthly Expenses: {format_currency(data['monthly_expenses'])}",
        f"Total Monthly EMI: {format_currency(data['total_monthly_emi'])}",
        f"Annual Tax (New Regime): {format_currency(data['tax_annual'])}",
        f"Net Monthly Income after tax: {format_currency(data['net_monthly_income_after_tax'])}",
        f"Monthly Surplus (available to save/invest): {format_currency(surplus)}",
        "---- Predictions (assuming 10% annual return on invested surplus)",
        f"Projected savings in 1 year: {format_currency(fv1)}",
        f"Projected savings in 5 years: {format_currency(fv5)}",
        f"Projected savings in 10 years: {format_currency(fv10)}",
        "---- Purchase Predictions",
        f"Car (₹10,00,000) in 5 years: {format_currency(carfv)} -> {'CAN AFFORD' if carok else 'CANNOT AFFORD'}",
        f"House down payment (₹5,00,000) in 5 years: {format_currency(housefv)} -> {'CAN AFFORD' if houseok else 'CANNOT AFFORD'}",
        f"Child education fund (₹15,00,000) in 10 years: {format_currency(childfv)} -> {'CAN AFFORD' if childok else 'CANNOT AFFORD'}",
        "---- Investment Suggestion",
        invest,
        "----",
    ]
    return "\n".join(lines)
def export_summaries(summary_text):
    
    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write(summary_text)
    #
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"summary_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"\nSaved latest summary to '{OUT_SUMMARY}' and archived as '{fname}'.\n")
def view_session_log(limit=20):
    if not os.path.exists(DATA_FILE):
        print("\nNo session log found (finance_data.csv).\n")
        return
    print(f"\nLast {limit} sessions from {DATA_FILE}:\n")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) <= 1:
        print("No sessions yet (only header or empty).\n")
        return
    header = lines[0].strip()
    rows = lines[1:]
    rows_to_show = rows[-limit:]
    print(header)
    for r in rows_to_show:
        print(r.strip())
    print()
def one_run():
    print("\nWho are you?")
    print("1) Student")
    print("2) Working Professional")
    choice = input("Enter choice (1 or 2): ").strip()
    if choice == "1":
        data = run_student_flow()
    elif choice == "2":
        data = run_worker_flow()
    else:
        print("Invalid choice. Returning to main prompt.")
        return None
    
    row = [
        datetime.datetime.now().isoformat(),
        data["user_type"],
        data["monthly_income"],
        data["monthly_expenses"],
        data["total_monthly_emi"],
        data["monthly_surplus"],
        data["net_monthly_income_after_tax"]
    ]
    append_session_row(row)

    summary = build_summary(data)
    print("\n" + summary + "\n")
    export_summaries(summary)
    return data
def main():
    print("=== Smart Personal Finance Planner & Investment Advisor ===")
    print("Reference: /mnt/data/BuildYourOwnProject Vidyarthi.pdf")
    try:
        while True:
            result = one_run()
            
            while True:
                print("What would you like to do next?")
                print(" r : Run another analysis")
                print(" v : View recent session log (finance_data.csv)")
                print(" q : Quit")
                action = input("Enter r / v / q: ").strip().lower()
                if action in ("r", "v", "q"):
                    break
                print("Please enter 'r', 'v', or 'q'.")
            if action == "r":
                continue
            elif action == "v":
                view_session_log(limit=20)
                RecursionError
                continue
            else:
                print("Thank you for using the Finance Planner!")
                break
    except KeyboardInterrupt:
        print("\nInterrupted. Thank you for using the Finance Planner!")
        try:
            sys.exit(0)
        except SystemExit:
            pass

if __name__ == "__main__":
    main()