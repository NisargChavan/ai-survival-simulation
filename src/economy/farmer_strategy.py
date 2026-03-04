from .market_strategy import MarketStrategy


class FarmerStrategy(MarketStrategy):

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

            return orders

        if crops > 1000:
            qty = 200
            orders.append(("sell","crops",qty))

        

        # Sell surplus crops
        if crops > 30:
            qty = min(10, max(0, int((crops - 30) * 0.25)))
            if qty > 0:
                orders.append(("sell", "crops", qty))
                
                
                
        

        # Buy wood for tools
        if woods < 30 or wood_price < 0.7:
            affordable = int(money // wood_price)
            qty = min(5, affordable)

            if qty > 0:
                orders.append(("buy", "woods", qty))

        return orders