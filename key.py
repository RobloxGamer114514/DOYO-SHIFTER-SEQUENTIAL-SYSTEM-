import pygame
import keyboard

# --------------------------
# 設定
# --------------------------
JOY_NAME = "DOYO"             # DOYOジョイスティック名
GEAR_BUTTONS = [0, 1, 2, 3, 4, 5]  # ギア1~6に対応するボタン番号
UP_KEY = "e"                  # 上りシフトキー
DOWN_KEY = "q"                # 下りシフトキー
# --------------------------

# pygame 初期化
pygame.init()
pygame.joystick.init()

# DOYOジョイスティックを探す
JOY_INDEX = None
for i in range(pygame.joystick.get_count()):
    js = pygame.joystick.Joystick(i)
    js.init()
    if JOY_NAME.lower() in js.get_name().lower():
        JOY_INDEX = i
        print(f"DOYO joystick found at index {JOY_INDEX}")
        break

if JOY_INDEX is None:
    raise RuntimeError("DOYO joystick not found!")

js = pygame.joystick.Joystick(JOY_INDEX)
js.init()

prev_valid_gear = 0  # 最後に押された有効ギア（1〜6）

# ギア取得（0~6）
def get_gear():
    for idx, btn in enumerate(GEAR_BUTTONS):
        if js.get_button(btn):
            return idx + 1  # ギア1~6
    return 0  # ニュートラルも返す

# --------------------------
# メインループ (最終安定版)
# --------------------------
print("Starting stable gear monitoring...")
while True:
    pygame.event.pump()
    gear = get_gear()  # 現在ギア（0〜6）
    
    # ニュートラル(0)の場合は、キー送信を行わず、次のループへ
    if gear == 0:
        continue

    # 1. 正常なシフトダウン判定（DOWN_KEYを最優先）
    # 直前のギアより現在のギアが低い場合
    if gear < prev_valid_gear:
        
        # 💥 誤判定防止ロジック
        # 3速以上からニュートラルを経由して1速に入った場合（例：3 -> 0 -> 1）のみ、DOWN_KEYを送信しない
        # これは、prev_valid_gearが2より大きく、gearが1である場合
        is_false_downshift_from_high_gear = (gear == 1 and prev_valid_gear > 2)
        
        if is_false_downshift_from_high_gear:
            # 3->0->1 の誤判定の場合、DOWN_KEYを避け、UP_KEYを送信して1速への移行を確定
            keyboard.send(UP_KEY)
        else:
            # 正常なダウンシフト（例: 3->2、または 2->1）の場合
            # 2->1 の直接シフトは、このelseブロックでDOWN_KEYが送られます
            keyboard.send(DOWN_KEY)
            
    # 2. 正常なシフトアップ判定
    elif gear > prev_valid_gear:
        # 正常なアップシフト（例: 1->2）
        keyboard.send(UP_KEY)

    # 3. 有効ギアの更新
    # キーが送られたかどうかに関わらず、非ニュートラルであれば更新
    prev_valid_gear = gear
