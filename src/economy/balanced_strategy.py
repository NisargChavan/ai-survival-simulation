from .market_strategy import MarketStrategy


class BalancedStrategy(MarketStrategy):

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
            qty = min(4, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

        # Sell surplus crops
        if crops > 150:
            qty = min(8, int((crops - 150) * 0.2))
            if qty > 0:
                orders.append(("sell", "crops", qty))

        # Sell surplus wood
        if woods > 70:
            qty = min(8, int((woods - 70) * 0.2))
            if qty > 0:
                orders.append(("sell", "woods", qty))


        if crop_price < 0.7:
            affordable = int(money//crop_price)
            qty = min (1,affordable)
            if qty > 0:
             orders.append(("buy","crops",qty))  

        # Buy crops if low
        if crops < 40:
            affordable = int(money // crop_price)
            qty = min(4, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

        # Buy wood if low
        if woods < 40:
            affordable = int(money // wood_price)
            qty = min(4, affordable)

            if qty > 0:
                orders.append(("buy", "woods", qty))

        return orders