import numpy as np
from numpy import log, polyfit, sqrt, std, subtract
import pandas as pd


def div0(a, b):
    """
    ignore / 0, and return 0 div0( [-1, 0, 1], 0 ) -> [0, 0, 0]
    credits to Dennis @ https://stackoverflow.com/questions/26248654/numpy-return-0-with-divide-by-zero
    """
    answer = np.true_divide(a, b)
    if not np.isfinite(answer):
        answer = 0
    return answer


def div_by_hundred(x):
    """ Divivde input by 100"""
    return x / 100.0


def discounted_value_cash_flow(cash_flow, periods_ahead, disc_rate):
    """
    Calculate discounted values of future cash flows
    :param cash_flow: np.Array future cash flows
    :param periods_ahead: integer of amounts of periods to look ahead
    :param disc_rate: np.Array of discount rates per period
    :return: np.Array of discounted future cash flows
    """
    return cash_flow / (1 + disc_rate)**periods_ahead


def find_horizon(dcfs):
    """
    Find index at which at which the discounted_cash flows can be cut off
    :param dcfs: list of discounted cash flows
    :return: index at which the list can be cut off
    """
    for idx, cash_flow in enumerate(dcfs):
        if cash_flow < 0.01:
            return idx
    return False


def calculate_npv(dividends, discount_rates):
    """Calculates the current NPV of a stream of dividends """
    current_index = 0
    final_index = len(dividends)
    discounted_cash_flows = dividends / ((1 + discount_rates)**range(current_index, final_index))
    if find_horizon(discounted_cash_flows):
        return sum(discounted_cash_flows[:find_horizon(discounted_cash_flows)])
    else:
        return np.nan


def hurst(ts):
    """
    source: https://www.quantstart.com/articles/Basics-of-Statistical-Mean-Reversion-Testing
    Returns the Hurst Exponent of the time series vector ts
    """
    # Create the range of lag values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


def organise_data(obs):
    """
    Extract data in managable format from list of orderbooks
    :param obs:
    :return:
    """
    burn_in_period = 100
    window = 20
    close_price = []
    returns = []
    autocorr_returns = []
    autocorr_abs_returns = []
    returns_volatility = []
    volume = []
    fundamentals = []
    for ob in obs:  # record
        # close price
        close_price.append(ob.tick_close_price[burn_in_period:])
        # returns
        r = pd.Series(np.array(ob.tick_close_price[burn_in_period:])).pct_change()
        returns.append(r)
        # autocorrelation returns
        ac_r = [r.autocorr(lag=lag) for lag in range(25)]
        autocorr_returns.append(ac_r)
        # autocorrelation absolute returns
        absolute_returns = pd.Series(r).abs()
        autocorr_abs_returns.append([absolute_returns.autocorr(lag=lag) for lag in range(25)])
        # volatility of returns
        roller_returns = r.rolling(window)
        returns_volatility.append(roller_returns.std(ddof=0))
        # volume
        volume.append([sum(volumes) for volumes in ob.transaction_volumes_history][burn_in_period:])
        # fundamentals
        fundamentals.append(ob.fundamental[burn_in_period:])
    mc_prices = pd.DataFrame(close_price).transpose()
    mc_returns = pd.DataFrame(returns).transpose()
    mc_autocorr_returns = pd.DataFrame(autocorr_returns).transpose()
    mc_autocorr_abs_returns = pd.DataFrame(autocorr_abs_returns).transpose()
    mc_volatility = pd.DataFrame(returns_volatility).transpose()
    mc_volume = pd.DataFrame(volume).transpose()
    mc_fundamentals = pd.DataFrame(fundamentals).transpose()

    return mc_prices, mc_returns, mc_autocorr_returns, mc_autocorr_abs_returns, mc_volatility, mc_volume, mc_fundamentals
