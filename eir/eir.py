from datetime import datetime
from dateutil.relativedelta import relativedelta

def generate_loan_repayment_schedule(loanstartdate, loanenddate, originalamount, repaymentfrequency, interestrate, upfrontfee):
    # Convert date strings to datetime objects
    loanstartdate = datetime.strptime(loanstartdate, '%Y-%m-%d')
    loanenddate = datetime.strptime(loanenddate, '%Y-%m-%d')
    
    # Calculate the number of months between start and end dates
    num_months = (loanenddate.year - loanstartdate.year) * 12 + loanenddate.month - loanstartdate.month
    
    # Define repayment intervals in months
    intervals = {
        'monthly': 1,
        'termly': 3,
        'quarterly': 3,
        'bi-annually': 6,
        'yearly': 12,
    }
    
    if repaymentfrequency not in intervals:
        raise ValueError("Invalid repayment frequency")
    
    repayment_interval = intervals[repaymentfrequency]
    
    # Calculate the number of repayments
    num_repayments = num_months // repayment_interval
    
    # Calculate the repayment amount per installment
    interest_amount = (interestrate / 100) * originalamount
    principal_per_installment = (originalamount - upfrontfee) / num_repayments
    
    # Generate the repayment schedule
    repayment_schedule = []
    running_balance = originalamount - upfrontfee
    current_date = loanstartdate
    for _ in range(num_repayments):
        interest_payment = (interestrate / 100) * running_balance
        principal_payment = principal_per_installment
        total_payment = interest_payment + principal_payment
        
        repayment_schedule.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'principal': principal_payment,
            'interest': interest_payment,
            'total_payment': total_payment,
            'running_balance': running_balance,
        })
        
        running_balance -= principal_payment
        current_date += relativedelta(months=repayment_interval)
    
    return repayment_schedule

# Example usage
loanstartdate = '2023-09-01'
loanenddate = '2024-09-01'
originalamount = 10000
repaymentfrequency = 'termly'  # Change to your desired frequency
interestrate = 5  # 5%
upfrontfee = 200

repayment_schedule = generate_loan_repayment_schedule(loanstartdate, loanenddate, originalamount, repaymentfrequency, interestrate, upfrontfee)
for entry in repayment_schedule:
    print(entry)


