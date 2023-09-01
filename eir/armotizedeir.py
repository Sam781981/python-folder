import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy_financial as npf
from scipy.optimize import brentq as root

def eirfunc(installment_amount,num_of_pmts,presVal):
    return root(lambda x:  installment_amount * ((1 - ((1 + x) ** (-num_of_pmts))) / x) - presVal, 0.000001, 0.999999) * 100 * 12

def generate_loan_repayment_schedule(loanstartdate, loanenddate, originalamount, repaymentfrequency,
                                     interestrate, upfrontfee, repaymenttype, interest_calculation_method,
                                     base_days, interest_type):
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
    
    # Determine the appropriate interest rate factor based on interest calculation method
    if interest_calculation_method == 'monthly':
        interest_rate_factor = interestrate / 100 / 12
    elif interest_calculation_method == 'daily':
        if base_days == 365:
            interest_rate_factor = interestrate / 100 / 365
        elif base_days == 360:
            interest_rate_factor = interestrate / 100 / 360
        else:
            raise ValueError("Invalid base days value")
    else:
        raise ValueError("Invalid interest calculation method")
    
    # Calculate the repayment amount per installment based on repayment type
    if repaymenttype == 'fpi':
        principal_per_installment = originalamount / num_repayments
    elif repaymenttype == 'emi':
        total_payment_per_installment = originalamount * (interest_rate_factor / (1 - (1 + interest_rate_factor) ** -num_repayments))
        principal_per_installment = originalamount / num_repayments
    else:
        raise ValueError("Invalid repayment type")
    

    
    # Generate the repayment schedule
    repayment_schedule = []
    running_balance = originalamount
    current_date = loanstartdate + relativedelta(months=repayment_interval)
    for _ in range(num_repayments):
        if interest_type == 'flatrate':
            interest_payment = interestrate / 100 * running_balance
        elif interest_type == 'variable':
            if interest_calculation_method == 'monthly':
                months_in_period = repayment_interval
                interest_payment = interestrate / 100 / 12 * running_balance * months_in_period
            elif interest_calculation_method == 'daily':
                days_in_period = (current_date - (current_date - relativedelta(months=repayment_interval))).days
                interest_payment = (interestrate / 100 / base_days) * days_in_period * running_balance
            else:
                raise ValueError("Invalid interest calculation method")
        else:
            raise ValueError("Invalid interest type")
        
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
    
    repayment_schedule_df = pd.DataFrame(repayment_schedule)
    eir = eirfunc(total_payment_per_installment, num_repayments, originalamount-upfrontfee)
    repayment_schedule_df['eir'] = eir
    repayment_schedule_df['eirschedule'] = npf.pmt(eir/100/repayment_interval,num_repayments,originalamount)
    return repayment_schedule_df

# Example usage
loanstartdate = '2023-01-31'
loanenddate = '2025-01-31'
originalamount = 10000
repaymentfrequency = 'quarterly'
interestrate = 5
upfrontfee = 200
repaymenttype = 'emi'
interest_calculation_method = 'daily'
base_days = 365
interest_type = 'variable'

repayment_schedule_df = generate_loan_repayment_schedule(
    loanstartdate, loanenddate, originalamount, repaymentfrequency, interestrate, upfrontfee, repaymenttype,
    interest_calculation_method, base_days, interest_type
)
print(repayment_schedule_df[['Principal', 'Interest', 'Total Payment']].sum())
print(repayment_schedule_df)
# repayment_schedule_df.to_csv('rep2.csv')
