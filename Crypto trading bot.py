
from dotenv import load_dotenv
import os
from binance.client import Client
import logging
import time
import argparse


load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


class BasicBot:
    def __init__(self, api_key, api_secret, symbol, buy_price, sell_price, quantity, order_type="MARKET", testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        self.symbol = symbol.upper()
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.quantity = quantity
        self.order_type = order_type.upper()
        self.in_position = False

        logging.basicConfig(level=logging.INFO, filename='trading_bot.log',
                            format='%(asctime)s:%(levelname)s:%(message)s')

    def get_current_price(self):
        try:
            ticker = self.client.futures_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            logging.error(f"Error fetching price: {e}")
            return None

    def place_market_order(self, side):
        try:
            order = self.client.futures_create_order(
                symbol=self.symbol,
                side=side,
                type='MARKET',
                quantity=self.quantity
            )
            logging.info(f"{side} MARKET order placed: {order}")
            print(f"{side} MARKET order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Error placing MARKET {side} order: {e}")
            print(f"Error placing MARKET {side} order: {e}")

    def place_stop_limit_order(self, side, stop_price, limit_price):
        try:
            order = self.client.futures_create_order(
                symbol=self.symbol,
                side=side,
                type='STOP',
                stopPrice=str(stop_price),
                price=str(limit_price),
                timeInForce='GTC',
                quantity=self.quantity
            )
            logging.info(f"{side} STOP-LIMIT order placed: {order}")
            print(f"{side} STOP-LIMIT order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Error placing STOP-LIMIT {side} order: {e}")
            print(f"Error placing STOP-LIMIT {side} order: {e}")

    def run(self):
        while True:
            price = self.get_current_price()
            if price is None:
                time.sleep(3)
                continue

            print(f"Current price of {self.symbol}: {price}")

            if not self.in_position and price < self.buy_price:
                print(f"Price is below {self.buy_price}. Preparing to BUY...")
                if self.order_type == "MARKET":
                    self.place_market_order('BUY')
                elif self.order_type == "STOP_LIMIT":
                    self.place_stop_limit_order('BUY', stop_price=price + 50, limit_price=price + 60)
                self.in_position = True

            elif self.in_position and price > self.sell_price:
                print(f"Price is above {self.sell_price}. Preparing to SELL...")
                if self.order_type == "MARKET":
                    self.place_market_order('SELL')
                elif self.order_type == "STOP_LIMIT":
                    self.place_stop_limit_order('SELL', stop_price=price - 50, limit_price=price - 60)
                self.in_position = False

            time.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Binance Futures Trading Bot')
    parser.add_argument('--symbol', type=str, default='BTCUSDT')
    parser.add_argument('--buy_price', type=float, required=True)
    parser.add_argument('--sell_price', type=float, required=True)
    parser.add_argument('--quantity', type=float, default=0.01)
    parser.add_argument('--order_type', type=str, choices=["MARKET", "STOP_LIMIT"], default="MARKET")

    args = parser.parse_args()

    bot = BasicBot(
        api_key=API_KEY,
        api_secret=API_SECRET,
        symbol=args.symbol,
        buy_price=args.buy_price,
        sell_price=args.sell_price,
        quantity=args.quantity,
        order_type=args.order_type
    )

    bot.run()
