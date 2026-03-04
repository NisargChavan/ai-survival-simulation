class MarketStrategy:
    
    def __init__(self,agent):
        self.agent = agent
        
         
    def decide_orders(self, market):
        
        raise NotImplementedError
    