from colorama import Fore, init
init(autoreset=True)

class Market:
    
     def __init__(self):
        
          self.prices = {
            "crops": 5,
            "woods": 4,
            "rare_crop": 40,
            "normal_farmer_tool" : 25,
            "special_farmer_tool" : 100
          
          }
          
          
          self.job_capacity = {
            "farmer": 2,
            "lumberjack": 2,
            "balanced": 2
        }
          
          self.base_price = self.prices.copy()
          
          self.sell_orders = {}
          self.buy_orders = {}
          self.market_history = []
          self.episode_history = []
          self.current_step = 0
          self.MAX_AGE = 40
          
    
     def sumbit_sell_order(self, agent, item, quantity):

      if quantity <= 0:
        return

    # Check inventory
      if agent.inventory.get(item, 0) < quantity:
        return

    # Limit total open orders
      if self.agent_has_open_order(agent, item, "sell"):
        return
    
      

      if item not in self.sell_orders:
        self.sell_orders[item] = []

      order = {
        "agent": agent,
        "qty": quantity,
        "age": 0
      }

      self.sell_orders[item].append(order)

    # Prevent order book explosion
      if len(self.sell_orders[item]) > 200:
        self.sell_orders[item].pop(0)

      print(Fore.CYAN + f"{agent.name} gave a sell order for {item} x{quantity}")
 
 
 
 
 
     def sumbit_buy_order(self, agent, item, quantity):

      if quantity <= 0:
        return

      if self.agent_has_open_order(agent, item, "buy"):
        return

      quantity = min(quantity, 50)

      if item not in self.buy_orders:
        self.buy_orders[item] = []

      order = {
        "agent": agent,
        "qty": quantity,
        "age": 0
    }

      self.buy_orders[item].append(order)

      if len(self.buy_orders[item]) > 600:
        self.buy_orders[item].pop(0)

      print(Fore.BLACK + f"{agent.name} gave a buy order for {item} x{quantity}")
          
        
    
     def update_prices(self):
        
        for item  in self.prices.keys():
            
            sellers = self.sell_orders.get(item,[])
            buyers = self.buy_orders.get(item,[])
            
            
            if not sellers and not buyers:
               continue
            
              
            supply = sum(order["qty"] for order in sellers)
            demand = sum(order["qty"] for order in buyers)
            if supply == 0:
                supply = 1
                            
            demand_ratio = (demand + 1) / (supply + 1)
            new_price = self.prices[item] * demand_ratio
            new_price = max(self.prices[item] * 0.9 , min(new_price,self.prices[item] * 1.1))
            
            
            
            
            self.prices[item] = (
                0.6 * self.prices[item] +
                0.4 * new_price
            )

            # Tool price cap
            if item == "normal_farmer_tool":
                self.prices[item] = min(self.prices[item], 40)

            if item == "special_farmer_tool":
                self.prices[item] = min(self.prices[item], 120)
            
            if item == "rare_crop":
                 self.prices[item] = min(self.prices[item], 80)    

            if demand == 0:
              demand = 1
           
            if self.prices[item] < 1.3:
               self.prices[item] = 1.3
                
                
                
     def get_market_trade_history(self):
           return  self.market_history      
    
    
     def age_and_clean_orders(self):

      for book in [self.sell_orders, self.buy_orders]:

        for item in list(book.keys()):
            new_orders = []

            for order in book[item]:
                order["age"] += 1

                if order["age"] <= self.MAX_AGE:
                    new_orders.append(order)

            book[item] = new_orders
    
    
    
     def clear_market(self):

      for item in self.prices.keys():

        sellers = self.sell_orders.get(item, [])
        buyers = self.buy_orders.get(item, [])

        if not sellers or not buyers:
            continue

        traded_pairs = set()

        price = self.prices[item]

        i = 0
        while i < len(sellers):

            sell_order = sellers[i]
            seller = sell_order["agent"]

            if sell_order["qty"] <= 0:
                sellers.pop(i)
                continue

            j = 0
            while j < len(buyers):

                buy_order = buyers[j]
                buyer = buy_order["agent"]

                if buy_order["qty"] <= 0:
                    buyers.pop(j)
                    continue

                if seller == buyer:
                    j += 1
                    continue


                trade_qty = min(sell_order["qty"], buy_order["qty"])

                actual_inventory = seller.inventory.get(item, 0)
                trade_qty = min(trade_qty, actual_inventory)

                cost = trade_qty * price

                if buyer.money < cost:
                    affordable = int(buyer.money // price)
                    trade_qty = min(trade_qty, affordable)
                    cost = trade_qty * price

                if trade_qty <= 0:
                    j += 1
                    continue

                # Execute trade
                seller.inventory[item] -= trade_qty
                seller.money += cost
                print(Fore.GREEN + f"{seller.name} sold {item} x{trade_qty} at {cost:.2f}")

                buyer.inventory[item] += trade_qty
                buyer.money -= cost
                print(Fore.GREEN + f"{buyer.name} bought {item} x{trade_qty} at {cost:.2f} ")
                
                if item == "normal_farmer_tool":
                  buyer.tool_durability["normal_farmer_tool"] = 50

                if item == "special_farmer_tool":
                  buyer.tool_durability["special_farmer_tool"] = 100


                # Log trade
                self.episode_history.append({
                    "step": self.current_step,
                    "seller": seller.name,
                    "buyer": buyer.name,
                    "item": item,
                    "quantity": trade_qty,
                    "price": round(price, 2)
                })

                sell_order["qty"] -= trade_qty
                buy_order["qty"] -= trade_qty

                if buy_order["qty"] <= 0:
                    buyers.pop(j)
                else:
                    j += 1

                if sell_order["qty"] <= 0:
                    break

            if sell_order["qty"] <= 0:
                sellers.pop(i)
            else:
                i += 1

        self.sell_orders[item] = sellers
        self.buy_orders[item] = buyers

      self.age_and_clean_orders()
      self.update_prices()
     
      
      
      
     def agent_has_open_order(self, agent, item, order_type):

      if order_type == "buy":
        orders = self.buy_orders.get(item, [])
      else:
        orders = self.sell_orders.get(item, [])

      for order in orders:
        if order["agent"] == agent:
            return True

      return False
  
  
     def count_agent_orders(self, agent):

      count = 0

      for item_orders in self.buy_orders.values():
        for order in item_orders:
            if order["agent"] == agent:
                count += 1

      for item_orders in self.sell_orders.values():
        for order in item_orders:
            if order["agent"] == agent:
                count += 1

      return count


     

    
market = Market()    
    
    