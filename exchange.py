import hashlib
import time
import requests
import hmac
import pandas as pd
from requests.exceptions import ReadTimeout

class tryminex:
    def __init__(self, apiKey='', secret=''):
        self.apiKey = apiKey
        self.secret = secret
        self.__base_url = 'https://api.tryminex.com'
        self.timeout = 3

    def __transfer_symbol(self, symbol):
        """transfer symbol format"""
        symbol = symbol.split('/')
        symbol = '_'.join(symbol)
        return symbol

    def __public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.__base_url + api_url
        try:
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            return
        if r.status_code == 200:
            return r.json()

    def __signed_GET(self, api_url, params={}, timeout=5):
        """request a signed url"""
        sign_str = ''
        for key in sorted(params.keys()):
            _ = '&' + key + '=' + str(params[key])
            sign_str += _
        payload_str = 'GET' + '&' + api_url + sign_str
        signature = hmac.new(bytes(self.secret, encoding='utf-8'), bytes(payload_str, encoding='utf-8'), digestmod=hashlib.sha256).hexdigest()
        params['sign'] = signature
        url = self.__base_url + api_url
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
        except ReadTimeout:
            print("get timeout")
            return
        except requests.exceptions.HTTPError as err:
            print(err)
            return
        if r.status_code == 200:
            return r.json()

    def __sign_POST(self, api_url, params, timeout):
        """request a signed url"""
        sign_str = ''
        for key in sorted(params.keys()):
            _ = '&' + key + '=' + str(params[key])
            sign_str += _
        payload_str = 'POST' + '&' + api_url + sign_str
        signature = hmac.new(bytes(self.secret, encoding='utf-8'), bytes(payload_str, encoding='utf-8'), digestmod=hashlib.sha256).hexdigest()
        params['sign'] = signature
        url = self.__base_url + api_url
        try:
            r = requests.post(url,data=params, timeout=timeout)
            r.raise_for_status()
        except ReadTimeout:
            print("post timeout")
            return
        except requests.exceptions.HTTPError as err:
            print(err)
            return
        if r.status_code == 200:
            return r.json()

    def load_markets(self):
        """load all symbols"""
        return self.__public_request('GET', '/api/v1/symbols')

    def fetch_markets_tickers(self):
        """Get tickers of all markets"""
        return self.__public_request('GET', '/api/v1/tickers')

    def fetch_tickers(self, symbol):
        """Get tickers of specific market"""
        symbol = self.__transfer_symbol(symbol)
        return self.__public_request('GET', '/api/v1/ticker/%s' % symbol)

    def fetch_depths(self, symbol, limit=50):
        """fetch depths information of specific symbol"""
        symbol = self.__transfer_symbol(symbol)
        return self.__public_request('GET', '/api/v1/depth?symbol=%s&limit=%d' % (symbol, limit))

    def fetch_ohlcv(self, symbol, period=1):
        """ Get OHLC(k line) of specific market."""
        symbol = self.__transfer_symbol(symbol)
        return self.__public_request('GET', '/api/v1/kline?symbol=%s&period=%d' % (symbol, period))

    def fetch_kline(self, symbol, period):
        """Same to fetch_ohlcv"""
        return self.fetch_ohlcv(symbol, period)

    def fetch_timestamp(self):
        """Get server current time, in seconds since Unix epoch"""
        return self.__public_request('GET', '/api/v1/timestamp')

    def user_info(self):
        """Get your profile and account info"""
        param = {}
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time()*1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/users/me', param, self.timeout)

    def accounts_info(self):
        """Get your accounts info"""
        param = {}
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time() * 1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/account/all', param, self.timeout)

    def currency_account(self, currency):
        """Get one of your specific accounts information"""
        param = {}
        param['currency'] = currency
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time() * 1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/account', param, self.timeout)

    def list_orders(self, symbol):
        """Get your orders, results is paginated"""
        param = {}
        param['symbol'] = self.__transfer_symbol(symbol)
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time() * 1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/processing-orders', param, self.timeout)

    def list_order(self, orderNo):
        """Get information of specified order"""
        param = {}
        param['orderNo'] = orderNo
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time() * 1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/order', param, self.timeout)

    def fetch_mytrades(self, symbol):
        """Get your executed trades. Trades are sorted in reverse creation order"""
        param = {}
        param['symbol'] = self.__transfer_symbol(symbol)
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time() * 1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/history-orders', param, self.timeout)

    def create_order(self, symbol, tradeType, price, amount):
        """Create a Sell/Buy order."""
        param = {
            'symbol': self.__transfer_symbol(symbol),
            'tradeType': tradeType,  #BUY/SELL
            'price': price,
            'amount': amount,
            'appid': self.apiKey,
            'nonce': int(time.time() * 1000),
            'timestamp': int(time.time())
        }
        return self.__sign_POST('/api/v1/order/create', param, self.timeout)

    def cancel_order(self, orderNo):
        """Cancel an order"""
        param = {}
        param['orderNo'] = orderNo
        param['appid'] = self.apiKey
        param['nonce'] = int(time.time() * 1000)
        param['timestamp'] = int(time.time())
        return self.__signed_GET('/api/v1/order/cancle', param, self.timeout)

    def cancel_all(self, symbol):
        x = self.list_orders(symbol)['data']
        df = pd.DataFrame(x)
        if len(df) > 0:
            order_list = list(df['orderNo'].values)
        else:
            print('No order found!')
            return None
        for order in order_list:
            print(order)
            self.cancel_order(order)
        print('All orders have been cancelled!!')
