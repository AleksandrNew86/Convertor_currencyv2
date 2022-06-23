import requests
import json
from config import available_currency


class APIException(Exception):
    pass


class GottenCurrency:
    @staticmethod
    def get_price(base, quote, amount):
        request_currency = requests.get(f'https://api.apilayer.com/fixer/convert?to={available_currency[quote][0]}\
&from={available_currency[base][0]}&amount={amount}', {"apikey": 'wabT2uTsxApcWjQdCN1ukNf1vGupRhUz'}).content
        result_conversion = json.loads(request_currency)["result"]
        result = round(float(result_conversion), 2)
        if amount < 1:
            from_ = available_currency[base][1]
        elif amount > 1:
            from_ = available_currency[base][2]
        else:
            from_ = base
        if result < 1:
            to_ = available_currency[quote][1]
        elif result > 1:
            to_ = available_currency[quote][2]
        else:
            to_ = quote
        return result, from_, to_, amount

