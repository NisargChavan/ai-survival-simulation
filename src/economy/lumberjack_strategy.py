from .market_strategy import MarketStrategy


class LumberJackStrategy(MarketStrategy):

    def decide_orders(self, market):

        orders = []

        crops = self.agent.inventory.get("crops", 0)
        woods = self.agent.inventory.get("woods", 0)
        food = self.agent.inventory.get("food", 0)
        normal_farming_tool = self.agent.inventory.get("normal_farmer_tool",0)
        normal_farming_tool_durability = self.agent.tool_durability.get("normal_farmer_tool_durability",0)
        special_farming_tool = self.agent.inventory.get("special_farmer_tool",0)
        speical_farming_tool_durability = self.agent.tool_durability.get("special_farmer_tool_durability",0)
        rare_crop = self.agent.inventory.get("rare_crop",0)
        
        expected_wood_yield = 4
        energy_cost = 3
        
        cost_per_wood = energy_cost / expected_wood_yield
        profit_margin = 1.4
                    
        crop_price = market.prices["crops"]
        wood_price = market.prices["woods"]
        rare_crop_price = market.prices["rare_crop"]
        special_farming_tool_price = market.prices["special_farmer_tool"]
        normal_farming_tool_price = market.prices["normal_farmer_tool"]

        money = self.agent.money

        # Emergency food
        if food < 5:
            affordable = int(money // crop_price)
            qty = min(30, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))
        
        if rare_crop < 3:
          orders.append(("buy","rare_crop",2))  
              
        
        if self.agent.money < 20:
           
            woods = self.agent.inventory.get("woods", 0)

            qty = int(woods * 0.2)
            if qty > 0:
              orders.append(("sell" , "woods",qty))
           
        
       
            
        if rare_crop_price < 30:
            budget = money * 0.2
            affordable = int(budget // rare_crop_price)
            
            qty = min (5,affordable)
            if qty > 0:
             orders.append(("buy","rare_crop",qty))    
             
        
             
        
                 
        
        
        
        if special_farming_tool == 1  and special_farming_tool_price > 70:
           qty = 1
           if qty > 0:
               orders.append(("sell","special_farmer_tool",qty))
               
        if normal_farming_tool > 0 and normal_farming_tool_price > 18 :      
           qty = 1
           if qty > 0:
               orders.append(("sell","normal_farmer_tool",qty))
               
               
        
               
                
        if wood_price > cost_per_wood * profit_margin and woods > 80:
            qty = min(40, int((woods - 80) * 0.25))
            if qty > 0:
                orders.append(("sell", "woods", qty))
                
        if crop_price < 1.5:
            budget = money * 0.2
            affordable = int(budget // crop_price)
            
            qty = min (20,affordable)
            if qty > 0:
             orders.append(("buy","crops",qty))          

        # Buy crops if low
        if crops < 20:
            affordable = int(money // crop_price)
            qty = min(40, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

        return orders