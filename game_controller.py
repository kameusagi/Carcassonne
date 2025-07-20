# controller/game_controller.py
import tkinter as tk
from functools import partial
from TileFactory import TileFactory
from board_renderer import BoardRenderer
from map import DynamicMap
from tile import Tile
from player import Player
import score_calculate
import tkinter.messagebox as messagebox

class GameController:
    def __init__(self, root):
        self.root = root
        self.map = DynamicMap()
        self.factory = TileFactory()
        self.build_ui()
        self.renderer = BoardRenderer(self.canvas)
        self.players = [ Player("player1", "red"), Player("player2", "blue") ]
        self.reset_game()

    def build_ui(self):
        # Canvas + スクロールバー
        self.canvas = tk.Canvas(self.root, bg="white")
        hbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = tk.Scrollbar(self.root, orient=tk.VERTICAL,   command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.config(xscrollincrement=1)
        self.canvas.config(yscrollincrement=1)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ステータスラベル
        self.status = tk.Frame(self.root)
        self.status.pack(side=tk.TOP, fill=tk.X)
        self.turn_label     = tk.Label(self.status, text="")
        self.phase_label    = tk.Label(self.status, text="")
        self.score_label    = tk.Label(self.status, text="")
        self.sub_label      = tk.Label(self.status, text="")
        self.meaple_label   = tk.Label(self.status, text="")
        self.tile_num_label  = tk.Label(self.status, text="")
        self.current_preview_meaple_celltype_label  = tk.Label(self.status, text="None")

        for w in (self.turn_label, self.phase_label,
                  self.score_label, self.sub_label,
                    self.meaple_label, 
                    self.tile_num_label,
                    self.current_preview_meaple_celltype_label):
            w.pack(side=tk.TOP, padx=7)
        self._bind_events()
        self._bind_btns()

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self.on_left_click) # 左クリックでタイル配置
        self.canvas.bind("<Button-3>", self.on_right_click) # 右クリックでタイル回転
        self.canvas.bind("<Motion>", self.on_mouse_move) # マウス移動でプレビュー更新
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)    # Linux scroll down
        # self.root.bind("<Key-plus>", lambda e: self.adjust_zoom(1))
        # self.root.bind("<Key-minus>", lambda e: self.adjust_zoom(-1))
        self.canvas.bind("<B1-Motion>", self.map_move) # ドラッグ中のマップ移動


    def _bind_btns(self):
        end_turn_btn = tk.Button(
            self.status,
            text="ターン終了",
            command=self.end_turn
        )
        end_turn_btn.pack(side=tk.TOP, padx=5, pady=5)

        discard_btn = tk.Button(
            self.status,
            text="タイルを捨てる",
            command=self.discard_tile
        )
        discard_btn.pack(side=tk.TOP, padx=5, pady=5)

        debug_btn = tk.Button(
            self.status,
            text="デバッグ",
            command=self.debug
        )
        debug_btn.pack(side=tk.TOP, padx=5, pady=5)
    
    def debug(self):
        pass

    def _place_initial_tile(self):
        init_tile = self.factory.next_tile(init=True)
        self.map.place_tile(3*Tile.SIZE, 3*Tile.SIZE, init_tile, init=True)
        self.current_preview_tile = self.factory.next_tile()
        self.renderer.render(self.map)
        self.update_labels()

    def update_labels(self):
        self.turn_label                             .config(text=f"Turn: {self.current_player.name}")
        self.phase_label                            .config(text=f"Phase: {self.phase}")
        self.tile_num_label                         .config(text=f"残り: {self.factory.tile_num}")
        self.current_preview_meaple_celltype_label  .config(text=f"cell_type: {self.current_preview_meaple_celltype}")
        # players が何人でも対応するスコア表記
        score_text   = "score: " + " | ".join(f"{p.name}: {p.score}"     for p in self.players)
        sub_text     = "sub_score: " + " | ".join(f"{p.name}: {p.score_sub}" for p in self.players)
        meaple_text  = "meaple_num: " + " | ".join(f"{p.name}: {p.get_stock_meaple()}" for p in self.players)

        self.score_label                            .config(text=score_text)
        self.sub_label                              .config(text=sub_text)
        self.meaple_label                           .config(text=meaple_text)

    def reset_game(self):
        self.turn = 0
        self.current_player = self.players[self.turn % len(self.players)]
        self.phase = 'tile'      # 'tile' or 'meaple'
        self.current_preview_meaple_celltype = "None"
        self._place_initial_tile()
        self.before_meaples = {}


    def _turn_phase_change(self):
        """
        ターンを進める処理。
        """
        self.renderer.render(self.map)

        # ターン交代 or フェーズ遷移
        if self.phase == 'tile':
            self.phase = 'meaple'
            self.update_labels()

        else:
            self.turn += 1
            self.current_player = self.players[self.turn % len(self.players)]
            self.phase = 'tile'
            self.update_labels()

            if self.factory.tile_num == 0:
                # ① 合計値（score + score_sub）の降順でソート
                sorted_players = sorted(
                    self.players,
                    key=lambda p: p.score + p.score_sub,
                    reverse=True
                )

                # ② 勝者を先頭に取り出し
                winner = sorted_players[0]

                # ③ 全員分の最終スコア行を組み立て
                msg_lines = []
                msg_lines.append(f"🏆 勝者: {winner.name} （{winner.score + winner.score_sub} 点）")
                msg_lines.append("")  # 空行
                for p in sorted_players:
                    total = p.score + p.score_sub
                    msg_lines.append(f"{p.name}: {total} 点  (score={p.score}, sub={p.score_sub})")

                # ④ ダイアログ表示
                tk.messagebox.showinfo("ゲーム終了", "\n".join(msg_lines))

                # ⑤ アプリ終了
                self.root.destroy()
                return
            

    def on_left_click(self, event):
        # --- タイル or ミープル配置処理 ---
        if self.phase == 'tile':
            self.before_meaples = {}
            placed = self._handle_tile_click(event)
            # セルのpatch_idsを更新
            self.map.update_cell_area()
            self.map.update_tile_area()
        else:
            placed = self._handle_meaple_click(event)

        if placed:
            # スコア計算＆ミープル回収
            self._score_calculation()
            self.map.collect_meaples()
            # ターン交代 or フェーズ遷移
            self._turn_phase_change()


        # 今のマウスの位置を保持
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_right_click(self, event):
        # プレビュー中のタイルだけ回転
        if self.phase == 'tile' and hasattr(self, 'current_preview_tile'):
            self.current_preview_tile.rotate()
            self.render_preview(event)
        elif self.phase == 'meaple':
            # ミープルの回転は無効
            print("ミープルの回転はできません")

    def _handle_tile_click(self, event):
        origin_x, origin_y = self.map.tile_origin_coords(event.x, event.y, self.canvas)

        placed = self.map.place_tile(origin_x, origin_y, self.current_preview_tile)
        if placed:
            self.current_preview_tile = self.factory.next_tile()
            return True
        else:
            return False

    def _handle_meaple_click(self, event):
        x0, y0 = self.map.cell_coords(event.x, event.y ,self.canvas)
        if self.current_player.stock_meaple <= 0:
            return True
        return self.map.place_meaple(x0, y0, self.current_player)

    def _score_calculation(self):
        score_calculate.score_calculation(self.players, self.map)
        pass

    def render_preview(self, event):
        if self.phase == 'tile':
            origin_x, origin_y = self.map.tile_origin_coords(event.x, event.y, self.canvas)
            self.renderer.render_preview(self.current_preview_tile,
                                          origin_x, origin_y,
                                            self.map.cell_size,
                                              self.phase,
                                              self.current_player.color)
            
            self.current_preview_meaple_celltype = "None"
        else:
            cell_x, cell_y = self.map.cell_coords(event.x, event.y, self.canvas)
            #そのセル位置にはなんのセルのタイプが置かれているかを出力
            if (cell_x, cell_y) in self.map.cells:
                cell = self.map.cells[(cell_x, cell_y)]
                self.current_preview_meaple_celltype = cell.cell_type

            self.renderer.render_preview(self.current_player,
                                          cell_x, cell_y,
                                            self.map.cell_size,
                                              self.phase,
                                              self.current_player.color)
        self.update_labels()

    def on_mouse_move(self, event):
        # プレビュー表示のために部分的に描画
        self.render_preview(event)
        pass

    def on_zoom(self, event):
        delta = 1 if event.delta > 0 else -1
        self.map.adjust_zoom(delta)
        self.renderer.render(self.map)


    def map_move(self, event):
        """
        マップをドラッグで移動する機能。
        マウスの動きに合わせてキャンバスをスクロールします。
        """
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        self.canvas.xview_scroll(-dx, "units")
        self.canvas.yview_scroll(-dy, "units")
        self.renderer.render(self.map)

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def discard_tile(self):
        """
        現在のプレビュータイルを捨てて、新しく factory から取得し直す
        """
        if self.phase != 'tile':
            print("タイルを捨てるのは、タイル配置フェーズのときだけです")
            return
        if not self.map.is_tile_anywhere_placeable(self.current_preview_tile): #タイルを置ける選択肢がない場合は、タイルを捨てる　Todo
            self.current_preview_tile = self.factory.next_tile()
            print(f"{self.current_player.name} がタイルを捨て、新しいタイルを取得しました。")
        else:
            pass

        self.update_labels()

    def end_turn(self):
        """
        ミープルを置きたくないときの処理
        """
        if self.phase == 'meaple':
            self._turn_phase_change()
        else:
            print("ミープル配置フェーズでのみ、ターン終了が可能です")
            pass
