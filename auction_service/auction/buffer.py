from collections import defaultdict
from threading import Lock

class BidBuffer:
    def __init__(self):
        self.buffer = defaultdict(list)  # auction_id → [(product_id, farmer_id, price)]
        self.lock = Lock()

    def add_bid(self, auction_id, product_id, farmer_id, price):
        with self.lock:
            self.buffer[str(auction_id)].append((product_id, farmer_id, price))

    def get_buffer(self, auction_id):
        with self.lock:
            return list(self.buffer[str(auction_id)])

    def clear_buffer(self, auction_id):
        with self.lock:
            self.buffer[str(auction_id)] = []

    def is_full(self, auction_id):
        with self.lock:
            return len(self.buffer[str(auction_id)]) >= 2
