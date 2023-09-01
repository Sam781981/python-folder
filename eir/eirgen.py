from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

def generate_loan_repayment_schedule(loanstartdate, loanenddate, originalamount, repaymentfrequency, interestrate, upfrontfee, repaymenttype):
    # Convert date strings to datetime objects
    loanstartdate = datetime.strptime(loanstartdate, '%Y-%m-%d')
    loanenddate = datetime.strptime(loanenddate, '%Y-%m-%d')
    
    # Calculate the number of months between start and end dates
    num_months = (loanenddate.year - loanstartdate.year) * 12 + loanenddate.month - loanstartdate.month
    
    # Define repayment intervals in months
    intervals = {
        'monthly': 1,
        'termly': 4,
        'quarterly': 3,
        'bi-annually': 6,
        'yearly': 12,
    }
    
    if repaymentfrequency not in intervals:
        raise ValueError("Invalid repayment frequency")
    
    repayment_interval = intervals[repaymentfrequency]
    
    # Calculate the number of repayments
    num_repayments = num_months // repayment_interval
    
    # Calculate the repayment amount per installment based on repayment type
    interest_amount = (interestrate / 100) * originalamount
    if repaymenttype == 'fpi':
        principal_per_installment = originalamount / num_repayments
    elif repaymenttype == 'emi':
        total_payment_per_installment = originalamount * (interestrate / 100) * (1 + (interestrate / 100)) ** num_repayments / \
                                       ((1 + (interestrate / 100)) ** num_repayments - 1)
        principal_per_installment = originalamount / num_repayments
    else:
        raise ValueError("Invalid repayment type")
    
    # Generate the repayment schedule
    repayment_schedule = []
    running_balance = originalamount
    current_date = loanstartdate
    for _ in range(num_repayments):
        interest_payment = (interestrate / 100) * running_balance
        if repaymenttype == 'emi':
            principal_payment = total_payment_per_installment - interest_payment
        else:
            principal_payment = principal_per_installment
        total_payment = interest_payment + principal_payment
        
        repayment_schedule.append({
            'Date': current_date,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Total Payment': total_payment,
            'Running Balance': running_balance,
        })
        
        running_balance -= principal_payment
        current_date += relativedelta(months=repayment_interval)
    
    return pd.DataFrame(repayment_schedule)

# Example usage
loanstartdate = '2023-09-01'
loanenddate = '2024-09-01'
originalamount = 10000
repaymentfrequency = 'termly'  # Change to your desired frequency
interestrate = 5  # 5%
upfrontfee = 200
repaymenttype = 'fpi'  # Change to 'emi' for Equal Monthly Installment

repayment_schedule_df = generate_loan_repayment_schedule(loanstartdate, loanenddate, originalamount, repaymentfrequency, interestrate, upfrontfee, repaymenttype)
print(repayment_schedule_df)
