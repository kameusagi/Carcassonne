class Player:
    MAX_STOCK_MEAPLE = 8

    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.stock_meaple = Player.MAX_STOCK_MEAPLE

    def get_stock_meaple(self):
        return self.stock_meaple

    def add_score(self, score: int):
        self.score += score

    def get_score(self):
        return self.score

    def put_meaple(self):
        if self.stock_meaple <= 0:
            print("メープルのストックがありません。")
        else:
            self.stock_meaple -= 1
            print(f"{self.name}さんがメープルを置きました。")

    def pull_meaple(self):
        if self.stock_meaple < Player.MAX_STOCK_MEAPLE:
            self.stock_meaple += 1
            print(f"{self.name}さんがメープルを回収しました。現在のストック: {self.stock_meaple}")
        else:
            print("メープルのストックは最大値に達しています。")
    
    # def can_put_meaple(self):
    #     return self.stock_meaple > 0
    
    
