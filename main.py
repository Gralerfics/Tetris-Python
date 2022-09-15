import pygame
import sys
import math
import random

from constants import *
from bricks import BRICKS


# ============================================ 函数定义 ============================================
def initWindow():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))             # 窗口创建与大小设置
    pygame.display.set_caption("Simple Tetris")                                 # 窗口标题
    return screen

def initGame():
    board = [MEDIUM_BIN] * ( BRICK_NUM_HEIGHT + 4 )                             # ( 高度 + 4 ) 行
    board.append(BOTTOM_BIN)                                                    # 底部
    return board

def nextIdx(idx):
    return idx - (idx % 4) + (idx + 1) % 4

def isAllowed(board, offset_x, offset_y, idx):
    # 获取物块并按 offset_x 左移位
    bck = tuple(x << offset_x for x in BRICKS[idx])

    # 判断边界 (指包括墙在内的边界, 如果正常调用该函数则不必要. 作示例用)
    # if offset_x < 0 or offset_y < 0:                                            # 判断顶部和右侧边界, 因为物块右上角为基准点
    #     return False
    # if offset_y + len(bck) - 1 > BRICK_NUM_HEIGHT + 3:                          # 判断底部边界
    #     return False
    # if max(bck) > BOTTOM_BIN:
    #     return False                                                            # 判断左侧边界, 如果物块移位后有部分数值 (位数) 超过底部行则说明超出
    
    # 判断是否有与现有物块重合
    for i in range(offset_y, offset_y + len(bck)):                              # 将物块与所占行的情况依次进行按位与操作，若不为零则说明有重合
        if (bck[i - offset_y] & board[i] != 0):
            return False

    # 都没问题返回允许
    return True

def randomBrick():                                                              # 随机新物块位置
    _idx = random.randint(0, len(BRICKS) - 1)                                   # randint() 参数指示闭区间
    _bck = BRICKS[_idx]
    _x = random.randint(3, BRICK_NUM_WIDTH + 3 - math.ceil(math.log2(max(_bck) + 1)) - 1)
    _y = 4 - len(_bck)
    return (_idx, _x, _y)

def paintScreen(board, screen):
    screen.fill((0, 0, 0))
    for _row in range(0, BRICK_NUM_HEIGHT):
        row = _row + 4
        for _col in range(0, BRICK_NUM_WIDTH):
            col = BRICK_NUM_WIDTH - 1 - _col + 3
            if board[row] & (1 << col) != 0:
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (_col * BRICK_SIZE + 2, _row * BRICK_SIZE + 2, BRICK_SIZE - 4, BRICK_SIZE - 4)
                )


# ============================================= 主程序 =============================================
if __name__ == "__main__":
    # 初始化
    screen = initWindow()
    board = initGame()
    
    last_time = 0
    inte_time = 0

    key_dict = {pygame.K_UP : False, pygame.K_DOWN : False, pygame.K_LEFT : False, pygame.K_RIGHT : False}

    now_idx = -1                                                                # 为 -1 则无方块正在下落
    now_x = -1
    now_y = -1

    # 主循环
    while True:
        # 事件处理
        for event in pygame.event.get():
            # 窗口关闭
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 键盘监听
            if event.type == pygame.KEYDOWN:
                key_dict[event.key] = True
            if event.type == pygame.KEYUP:
                key_dict[event.key] = False
        
        # 时间检测
        now_time = pygame.time.get_ticks()

        #  - 按键间隔时间检测
        if (now_time - inte_time >= KEY_TIME_INTERVAL):
            inte_time = now_time
            if now_idx >= 0:
                if key_dict[pygame.K_UP]:
                    if isAllowed(board, now_x, now_y, nextIdx(now_idx)):
                        now_idx = nextIdx(now_idx)
                if key_dict[pygame.K_DOWN]:
                    if isAllowed(board, now_x, now_y + 1, now_idx):
                        now_y += 1
                    else:
                        _bck = tuple(x << now_x for x in BRICKS[now_idx])
                        for i in range(now_y, now_y + len(BRICKS[now_idx])):
                            board[i] |= _bck[i - now_y]
                        now_idx = -1
                if key_dict[pygame.K_LEFT]:
                    if isAllowed(board, now_x + 1, now_y, now_idx):
                        now_x += 1
                if key_dict[pygame.K_RIGHT]:
                    if isAllowed(board, now_x - 1, now_y, now_idx):
                        now_x -= 1

        #  - 下落时间检测
        if (now_time - last_time >= TIME_INTERVAL):
            last_time = now_time
            if now_idx < 0:
                # 新物块
                (now_idx, now_x, now_y) = randomBrick()
            else:
                # 自然下落
                if isAllowed(board, now_x, now_y + 1, now_idx):
                    # 允许下落
                    now_y += 1
                else:
                    # 不允许下落
                    _bck = tuple(x << now_x for x in BRICKS[now_idx])           # 就位
                    for i in range(now_y, now_y + len(BRICKS[now_idx])):        # 落地
                        board[i] |= _bck[i - now_y]
                    now_idx = -1

        # 规则检查
        for _row in range(0, BRICK_NUM_HEIGHT):
            row = _row + 4
            if board[row] == BOTTOM_BIN:                                        # 行满
                del(board[row])
                board[:0] = [MEDIUM_BIN]
        
        # 绘制 (可以在屏幕内容变化时才更新, 这里就草率点吧)
        board_tmp = board.copy()
        if now_idx >= 0:
            _bck = tuple(x << now_x for x in BRICKS[now_idx])
            for i in range(now_y, now_y + len(BRICKS[now_idx])):
                board_tmp[i] |= _bck[i - now_y]
        paintScreen(board_tmp, screen)

        # 更新
        pygame.display.flip()
