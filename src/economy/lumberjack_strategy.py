from .market_strategy import MarketStrategy


class LumberJackStrategy(MarketStrategy):

    def decide_orders(self, market):

        orders = []

        crops = self.agent.inventory.get("crops", 0)
        woods = self.agent.inventory.get("woods", 0)
        food = self.agent.inventory.get("food", 0)

        crop_price = market.prices["crops"]
        wood_price = market.prices["woods"]

        money = self.agent.money

        # Emergency food
        if food < 5:
            affordable = int(money // crop_price)
            qty = min(5, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

        # Sell surplus wood
        if woods > 80:
            qty = min(10, int((woods - 80) * 0.25))
            if qty > 0:
                orders.append(("sell", "woods", qty))
                
        if crop_price < 0.7:
            affordable = int(money//crop_price)
            qty = min (1,affordable)
            if qty > 0:
             orders.append(("buy","crops",qty))          

        # Buy crops if low
        if crops < 20:
            affordable = int(money // crop_price)
            qty = min(5, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

        return orders