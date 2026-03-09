class ProfitEvaluator:
    
    def __init__(self,market):
        self.market = market
        
    
    
    def evaluate_farmer_profit(self,agent , profession_counts):
        
        crop_pirce = self.market.prices['crops'] * agent.price_bias
    
        
        expected_crop_yield = 7
        
        energy_cost = 4
        
        base_profit = expected_crop_yield * crop_pirce - energy_cost
        
        farmers = profession_counts["farmer"]
        
        competition_penalty = 1 + farmers * 0.5

        
        return base_profit / competition_penalty 
    
    def evaluate_lumberjack_profit(self,agent,profession_counts):
        
        
        wood_price = self.market.prices['woods'] * agent.price_bias
        
        expected_wood_yield = 4
        energy_cost = 3
        
        base_profit = expected_wood_yield * wood_price - energy_cost
        lumberjacks = profession_counts["lumberjack"]

        competition_penalty = 1 + lumberjacks * 0.5
        

        return base_profit / competition_penalty
    
    
    def evaluate_balanced_profit(self,agent,profession_counts):
        
        crop_price = self.market.prices['crops']  * agent.price_bias
        wood_price = self.market.prices['woods'] * agent.price_bias
        
        expected_crop_yield = 2
        expected_wood_yield = 1
        balanced = profession_counts["balanced"]
       
        revenue = (crop_price * expected_crop_yield) + (wood_price * expected_wood_yield)
        
        competition_penalty = 1 + balanced * 0.5
        
        
        return revenue / competition_penalty
    
    
    def evaluate_all(self,agent,profession_counts):
        
        profits = {}
        
        profits['farmer'] = self.evaluate_farmer_profit(agent,profession_counts)
        profits['lumberjack'] = self.evaluate_lumberjack_profit(agent,profession_counts)
        profits['balanced'] = self.evaluate_balanced_profit(agent,profession_counts)
        
        return profits
        
        