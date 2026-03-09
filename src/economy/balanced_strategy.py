from .market_strategy import MarketStrategy


class BalancedStrategy(MarketStrategy):

    def decide_orders(self, market):

        orders = []

        crops = self.agent.inventory.get("crops", 0)
        woods = self.agent.inventory.get("woods", 0)
        food = self.agent.inventory.get("food", 0)
        normal_farming_tool_durability = self.agent.tool_durability.get("normal_farmer_tool_durability",0)
        special_farming_tool = self.agent.inventory.get("special_farmer_tool",0)
        speical_farming_tool_durability = self.agent.tool_durability.get("special_farmer_tool_durability",0)
        rare_crop = self.agent.inventory.get("rare_crop",0)
        normal_farming_tool = self.agent.inventory.get("normal_farmer_tool",0)

        crop_price = market.prices["crops"]
        wood_price = market.prices["woods"]
        rare_crop_price = market.prices["rare_crop"]
        special_farming_tool_price = market.prices["special_farmer_tool"]
        normal_farming_tool_price = market.prices["normal_farmer_tool"]
        
        crop_cost = 0.70
        wood_cost = 1.33
        profit_margin = 1.4
        
        money = self.agent.money

        # Emergency food
        if food < 5:
            affordable = int(money // crop_price)
            qty = min(20, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))
                
        
        if special_farming_tool > 0 and special_farming_tool_price > 70:
           qty = 1
           if qty > 0:
               orders.append(("sell","special_farmer_tool",qty))
               
        if normal_farming_tool > 0 and normal_farming_tool_price > 18 :      
           qty = 1
           if qty > 0:
               orders.append(("sell","normal_farmer_tool",qty))
               
        if rare_crop <= 0:
            budget = money * 0.2
            affordable = int(budget // rare_crop_price)
            qty = min(3, affordable)
            orders.append(("buy","rare_crop",qty))       
               
               
        qty = 0

        if rare_crop > 10 and rare_crop_price > 30:
            qty = max(1, int(rare_crop * 0.7))

        elif rare_crop > 3 and rare_crop_price > 30:
            qty = max(1, int(rare_crop * 0.4))

        elif rare_crop >= 1 and rare_crop_price > 25:
            qty = 1

        if qty > 0:
            orders.append(("sell","rare_crop",qty))       
                        
       
        if rare_crop_price < 30:
            budget = money * 0.2
            affordable = int(budget // rare_crop_price)
            
            qty = min (5,affordable)
            if qty > 0:
             orders.append(("buy","rare_crop",qty))                    
                
        
        if self.agent.money < 20:
           
            woods = self.agent.inventory.get("woods", 0)
            crops = self.agent.inventory.get("crops", 0)
            
            crop_qty = int(crops * 0.15)
            wood_qty = int(woods * 0.15)

            if crop_qty > 0:
              orders.append(("sell", "crops", crop_qty))

            if wood_qty > 0:
              orders.append(("sell", "woods", wood_qty))
            
            
                    
                
        if crops > 50 and crop_price > crop_cost * profit_margin:
            qty = min(40, int((crops - 50) * 0.2))
            if qty > 0:
             orders.append(("sell", "crops", qty))
         

        
        if woods > 30 and wood_price > wood_cost * profit_margin:
            qty = min(40, int((woods - 30) * 0.2))
            if qty > 0:
                orders.append(("sell", "woods", qty))


        if crop_price < 1.5:
            budget = money * 0.2
            affordable = int(budget // crop_price)
            qty = min (40,affordable)
            if qty > 0:
             orders.append(("buy","crops",qty))  
             
        if wood_price < 1.5:
            budget = money * 0.2
            affordable = int(budget //wood_price)
            qty = min (40,affordable)
            if qty > 0:
             orders.append(("buy","woods",qty))       

        # Buy crops if low
        if crops < 30:
            affordable = int(money // crop_price)
            qty = min(4, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

        # Buy wood if low
        if woods < 30:
            affordable = int(money // wood_price)
            qty = min(40, affordable)

            if qty > 0:
                orders.append(("buy", "woods", qty))

        return orders