import hashlib
import time
import requests
import hmac

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
        # symbol.reverse()
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
        if r.status_code == 200:
            return r.json()

    def __signed_GET(self, api_url, params={}, timeout = 5):
        """request a signed url"""

        sign_str = ''
        for key in sorted(params.keys()):
            _ = '&' + key + '=' + str(params[key])
            sign_str += _

        payload_str = 'GET' + '&' + api_url + sign_str
        signature = hmac.new(self.secret, payload_str,digestmod=hashlib.sha256).hexdigest()
        params['sign'] = signature

        url = self.__base_url + api_url
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
        except ReadTimeout:
            print "get timeout"
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
        if r.status_code == 200:
            return r.json()

    def __sign_POST(self, api_url, params, timeout):
        """request a signed url"""
        sign_str = ''
        for key in sorted(params.keys()):
            _ = '&' + key + '=' + str(params[key])
            sign_str += _
        payload_str = 'POST' + '&' + api_url + sign_str
        signature = hmac.new(self.secret, payload_str,digestmod=hashlib.sha256).hexdigest()
        params['sign'] = signature

        url = self.__base_url + api_url
        try:
            r = requests.post(url,data=params, timeout=timeout)
            r.raise_for_status()
        except ReadTimeout:
            print "post timeout"
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)

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
        return self.__signed_GET('/api/v1/processing-orders', param)

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
            'symbol':self.__transfer_symbol(symbol),
            'tradeType':tradeType,
            'price':price,
            'amount':amount,
            'appid':self.apiKey,
            'nonce':int(time.time() * 1000),
            'timestamp':int(time.time())
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

apiKey = '123456789'
secret = '123456789'

tmx = tryminex(apiKey, secret)
symbol = 'TMX/USDT'
#print(tmx.load_markets())
#print(tmx.fetch_depths(symbol))
#print(tmx.fetch_tickers(symbol))
#print(tmx.fetch_markets_tickers())
#print(tmx.fetch_kline(symbol, 30))
#print(tmx.fetch_ohlcv(symbol, 1))
print(tmx.fetch_timestamp())

print(tmx.user_info())
#print(tmx.accounts_info())
#print(tmx.currency_account('TMX'))
#print(tmx.list_orders('TMX/USDT'))
#print(tmx.list_order('123456789'))
#print(tmx.fetch_mytrades('TMX/USDT'))
#print(tmx.create_order(symbol='TMX/USDT', tradeType='BUY', price='0.1', amount='1'))
#print(tmx.cancel_order('123456789'))
