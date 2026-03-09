from .market_strategy import MarketStrategy
from .ProfitEvaluator import ProfitEvaluator

class FarmerStrategy(MarketStrategy):

    def decide_orders(self, market):

        orders = []
        
        
        special_tool = self.agent.inventory.get("special_farmer_tool", 0)
        normal_tool = self.agent.inventory.get("normal_farmer_tool", 0)
        
        
        expected_crop_yield = 7

        if special_tool > 0:
            expected_crop_yield = int(expected_crop_yield * 1.5)
        
        if normal_tool > 0:
            expected_crop_yield = int(expected_crop_yield * 1.2)    
            
        
        
       
        energy_cost = 4

        cost_per_crop = energy_cost / expected_crop_yield
        profit_margin = 1.4

        crops = self.agent.inventory.get("crops", 0)
        woods = self.agent.inventory.get("woods", 0)
        food = self.agent.inventory.get("food", 0)
        normal_farming_tool = self.agent.inventory.get("normal_farmer_tool",0)
        special_farming_tool = self.agent.inventory.get("special_farmer_tool",0)
      
        rare_crop = self.agent.inventory.get("rare_crop",0)
        
        
        
        
        

        crop_price = market.prices["crops"]
        wood_price = market.prices["woods"]
        rare_crop_price = market.prices["rare_crop"]

        money = self.agent.money

        # Emergency food
        if food < 5:
            affordable = int(money // crop_price)
            qty = min(40, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))

            return orders
        
        if self.agent.money < 20:
           
            crops = self.agent.inventory.get("crops", 0)

            qty = int(crops * 0.2)
            if qty > 0: 
              orders.append(("sell" , "crops",qty))
              
              
        qty = 0

        if rare_crop > 10 and rare_crop_price > 28:
            qty = max(1, int(rare_crop * 0.7))

        elif rare_crop > 3 and rare_crop_price > 28:
            qty = max(1, int(rare_crop * 0.4))

        elif rare_crop >= 1 and rare_crop_price > 25:
            qty = 1

        if qty > 0:
            orders.append(("sell","rare_crop",qty))
                
                    
        
        
        
        if normal_farming_tool <= 0:
            qty = 1
            orders.append(("buy","normal_farmer_tool",qty))
            
        if special_farming_tool <= 0:
            qty = 1
            orders.append(("buy","special_farmer_tool",qty)) 
            
                  
            
            
        
                
        if crop_price > cost_per_crop * profit_margin and crops > 30:

            qty = min(40, int((crops - 30) * 0.3))

            if qty > 0:
             orders.append(("sell", "crops", qty))
             
             


        # if crops > 100:
        #     qty = 40
        #     orders.append(("sell","crops",qty))

        

        # # Sell surplus crops
        # if crops > 30:
        #     qty = min(10, max(0, int((crops - 30) * 0.25)))
        #     if qty > 0:
        #         orders.append(("sell", "crops", qty))
                
         
        if crop_price < 1.5:

            budget = money * 0.2
            affordable = int(budget // crop_price)

            qty = min(20, affordable)

            if qty > 0:
                orders.append(("buy", "crops", qty))         
                  
                  
    
        # Buy wood for tools
        if woods < 30 or wood_price < 1.5:
            affordable = int(money // wood_price)
            qty = min(40, affordable)

            if qty > 0:
                orders.append(("buy", "woods", qty))

        return orders
    
    
