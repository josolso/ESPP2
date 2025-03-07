import pytest
from importlib.resources import files
from rich.console import Console
from rich.table import Table

from espp2.datamodels import Transactions, Dividend, EntryTypeEnum, Amount, Deposit, Wire
from espp2.positions import Positions, Cash
from espp2.main import tax_report
import json
import logging
import datetime


def test_dividends(caplog):
    caplog.set_level(logging.INFO)
    # Create a dividend object
    transactions = []

    transactions.append(Deposit(type=EntryTypeEnum.DEPOSIT, date='2022-08-26', symbol='CSCO',
            qty=100, purchase_date='2022-10-26', 
            purchase_price=Amount(currency='USD', value=10, nok_value=100, nok_exchange_rate=10),
            description='', source='test'))

    transactions.append(Deposit(type=EntryTypeEnum.DEPOSIT, date='2022-10-10', symbol='CSCO',
            qty=100, purchase_date='2022-10-26', 
            purchase_price=Amount(currency='USD', value=10, nok_value=100, nok_exchange_rate=10),
            description='', source='test'))

    d = Dividend(type=EntryTypeEnum.DIVIDEND, date='2022-10-26', symbol='CSCO',
                 amount=Amount(currency='USD', value=38, nok_value=100, nok_exchange_rate=10),
                 source='test')
    assert(d.exdate == datetime.date(2022, 10, 4))
    transactions.append(d)

    t = Transactions(transactions=transactions)
    # c = Cash(2022, t.transactions, None)
    p = Positions(2022, None, t.transactions)
    dividends = p.dividends()
    assert dividends[0].symbol == 'CSCO'
    assert dividends[0].amount.value == 38
    for record in caplog.records:
        if record.funcName == 'dividends':
            assert record.message == "Total shares of CSCO at dividend date: 100 dps: 0.38 reported: 0.38"


def test_wire():
    #  type=<EntryTypeEnum.WIRE: 'WIRE'> date=datetime.date(2022, 11, 25)
    #  amount=Amount(currency='USD', nok_exchange_rate=Decimal('9.9263'),
    #                 nok_value=Decimal('-243548'), value=Decimal('-24535.66')) 
    #  description='Cash Disbursement' fee=Amount(currency='USD', 
    #                                             nok_exchange_rate=Decimal('9.9263'), nok_value=Decimal('-148.894'), value=Decimal('-15.00')) source='schwab:../Stocks/data/EquityAwardsCenter_Transactions_20221222153044.csv' id='WIRE 2022-11-25:1'

    w = Wire(type=EntryTypeEnum.WIRE, date='2022-11-25',
             amount=Amount(currency='USD', value=-24535.66, nok_value=-243548, nok_exchange_rate=9.9263),
             source='test',
             description='Cash Disbursement',)
    
    assert w.fee == None