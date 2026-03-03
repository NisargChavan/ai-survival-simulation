from colorama import Fore, init
init(autoreset=True)

class Market:
    
     def __init__(self):
        
          self.prices = {
            "crops": 5,
            "woods": 4,
            "rare_crop": 15
          }
          
          self.base_price = self.prices.copy()
          
          self.sell_orders = {}
          self.buy_orders = {}
          self.market_history = []
          self.episode_history = []
          self.current_step = 0
          
    
     def sumbit_sell_order(self,agent,item,quantity):
        if quantity <= 0:
           return
        
        if agent.inventory.get(item,0) >= quantity:
            
            self.sell_orders.setdefault(item,[]).append((agent,quantity))
            
            if len(self.sell_orders[item]) > 200:
                self.sell_orders[item].pop(0)
          
     def sumbit_buy_order(self,agent,item,quanatiy):
        if quanatiy <=0:
            return
        
        price = self.prices[item]
        max_affordable = int(agent.money // price)     
        quanatiy = min(quanatiy,max_affordable) 
        
        if quanatiy > 0:

            self.buy_orders.setdefault(item, []).append((agent, quanatiy))
            
            if len(self.buy_orders[item]) > 200:
                self.buy_orders[item].pop(0)
          
        
    
     def update_prices(self):
        
        for item  in self.prices.keys():
            
            sellers = self.sell_orders.get(item,[])
            buyers = self.buy_orders.get(item,[])
            
            
            if not sellers and not buyers:
               continue
            
            supply = sum(q for _, q in sellers)
            demand = sum(q for _, q in buyers)

            if supply == 0:
                supply = 1
                            
            demand_ratio = (demand + 1) / (supply + 1)
            new_price = self.base_price[item] * demand_ratio
            
            
            
            
            self.prices[item] = (
                0.8 * self.prices[item] +
                0.2 * new_price
            )

            if demand == 0:
              demand = 1
           
            if self.prices[item] < 0.5:
                self.prices[item] = 0.5
                
                
                
     def get_market_trade_history(self):
           return  self.market_history      
    
    
    
     def clear_market(self):

    # First update prices based on submitted orders
      self.update_prices()

      for item in self.prices.keys():

        sellers = self.sell_orders.get(item, [])
        buyers = self.buy_orders.get(item, [])

        if not sellers or not buyers:
            continue

        # Make mutable copies
        remaining_supply = [(s, q) for s, q in sellers]
        remaining_demand = [(b, q) for b, q in buyers]

        price = self.prices[item]

        # Try matching every seller with every buyer
        for s_index in range(len(remaining_supply)):

            seller, sell_qty = remaining_supply[s_index]

            if sell_qty <= 0:
                continue

            for b_index in range(len(remaining_demand)):

                buyer, buy_qty = remaining_demand[b_index]

                if buy_qty <= 0:
                    continue

                if seller == buyer:
                    continue  # Prevent self trade

                trade_qty = min(sell_qty, buy_qty)

                # ---- SELLER INVENTORY SAFETY CHECK ----
                actual_inventory = seller.inventory.get(item, 0)
                if actual_inventory < trade_qty:
                    trade_qty = actual_inventory

                if trade_qty <= 0:
                    continue

                cost = trade_qty * price

                # ---- BUYER AFFORDABILITY CHECK ----
                if buyer.money < cost:
                    affordable_qty = int(buyer.money // price)
                    if affordable_qty <= 0:
                        continue
                    trade_qty = min(trade_qty, affordable_qty)
                    cost = trade_qty * price

                if trade_qty <= 0:
                    continue

                # ---- EXECUTE TRADE ----
                seller.inventory[item] -= trade_qty
                seller.money += cost

                buyer.inventory[item] += trade_qty
                buyer.money -= cost

                # ---- LOG TRADE ----
                self.episode_history.append({
                    "step": self.current_step,
                    "seller": seller.name,
                    "buyer": buyer.name,
                    "item": item,
                    "quantity": trade_qty,
                    "price": round(price, 2)
                })

                # ---- UPDATE REMAINING ORDER QUANTITIES ----
                sell_qty -= trade_qty
                buy_qty -= trade_qty

                remaining_supply[s_index] = (seller, sell_qty)
                remaining_demand[b_index] = (buyer, buy_qty)

                if sell_qty <= 0:
                    break  # Seller exhausted, move to next seller

    # Clear order book after matching
      self.sell_orders.clear()
      self.buy_orders.clear()