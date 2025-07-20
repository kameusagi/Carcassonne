import os

class Player:
    MAX_STOCK_MEAPLE = 10

    def __init__(self, name: str, color: str):
        self.name = name
        self.score = 0
        self.score_sub = 0
        self.color = color
        self.meaple_path = os.path.join("./ミープル", color + ".jpg")
        self.stock_meaple = Player.MAX_STOCK_MEAPLE

    def get_stock_meaple(self):
        return self.stock_meaple

    def get_score(self):
        return self.score

    def get_subscore(self):
        return self.score_sub

    def put_meaple(self):
        if self.stock_meaple <= 0:
            return False
        else:
            self.stock_meaple -= 1
            return True

    def pull_meaple(self):
        if self.stock_meaple < Player.MAX_STOCK_MEAPLE:
            self.stock_meaple += 1
        else:
            print("メープルのストックは最大値に達しています。")
    
    # def can_put_meaple(self):
    #     return self.stock_meaple > 0
    
    
