from datetime import date
import calendar

CUT_DAYS = [8, 18, 28]


def calculate_expiry(payment_date: date) -> date:
    """
    Given a payment date, find the nearest cut day (8, 18, 28).
    Ties are broken by choosing the larger cut day.
    If the resulting cut day has already passed in the current month
    (strictly less than payment_date), move to the same cut day next month.
    """
    best_cut = None
    best_diff = float('inf')

    for cut in CUT_DAYS:
        diff = abs(payment_date.day - cut)
        if diff < best_diff or (diff == best_diff and cut > best_cut):
            best_diff = diff
            best_cut = cut

    year = payment_date.year
    month = payment_date.month

    expiry = date(year, month, best_cut)

    # Strictly less than: if cut day already passed, move to next month
    if expiry < payment_date:
        if month == 12:
            expiry = date(year + 1, 1, best_cut)
        else:
            expiry = date(year, month + 1, best_cut)

    return expiry


def calculate_multi_month_expiry(start_date: date, months: int) -> date:
    """
    Iteratively apply calculate_expiry for N months.
    When the start date IS already a cut day, calculate_expiry returns the same
    date (valid – not yet passed). In that case we advance to the same cut day
    in the next calendar month so that each iteration actually moves forward.
    """
    current = start_date
    for _ in range(months):
        expiry = calculate_expiry(current)
        if expiry == current:
            # Already on a cut day; advance to the same cut day next month
            if current.month == 12:
                current = date(current.year + 1, 1, current.day)
            else:
                current = date(current.year, current.month + 1, current.day)
        else:
            current = expiry
    return current
