#-------------------------------------------------------------------------------
# Name:        qLearning
# Purpose:
#
# Author:      TOMOKIYO Hisayoshi
#
# Created:     01/08/2014
# Copyright:   (c) TOMOKIYO Hisayoshi 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8
#-------------------------------------------------------------------------------
import copy
import random

POINT_Y=0
POINT_X=1
DIRECTION=2

RELATIVE_DIRECTION = ("FRONT","RIGHT","BACK","LEFT")#相対方向

ACTIO= (
        "FORWARD_MARCH",    #前に進め
        "BACKWARD_MARCH",   #後ろに進め
        "RIGHT_FACE",       #右向け右
        "LEFT_FACE",        #左向け左
        )

#*******************************************************************************
class MazeInfo (object):
    """ 迷路クラス

        定数の説明
        START：開始位置
        GAOL ：終了位置
        FACE ：開始時のエージェントの向き
        MAZE ：迷路情報

    """

    START =(3,1)
    GAOL =(2,5)
    FACE = "SOUTH"
    MAZE = """
    ┏┳┳━━━┓
    ┣┻┛　　　┃
    ┃　　　┃　┃
    ┃　┃　┃　┃
    ┣┳┫　　　┃
    ┗┻┻━━━┛
    """
    #-------------------------------------------------------------------------------
    def __init__(self,maze=MAZE):
        self.maze =maze
        self._setMaseList()
    #-------------------------------------------------------------------------------
    def _setMaseList(self):
        """ 迷路(self.maze)を2次元リストに分解
        """
        self.mazeList=[]
        for line in self.maze.split("\n"):
            if line.strip() != "":
                   self.mazeList.append(list(line.strip()))

    #-------------------------------------------------------------------------------
    def display(self,titel,state = [0,0,"FRONT"]):
        """ 迷路に開始地点、終了地点、エージェントを記入して出力する
        """
        displayList = copy.deepcopy(self.mazeList)

        #ゴールを代入
        displayList[self.GAOL[POINT_Y]][self.GAOL[POINT_X]] = "終"


        #絶対情報に変換
        abState = self._chgRelativeToAbsolute(state)

        #向き決定
        FACE = {"NORTH":"↑","EAST":"→","SOUTH":"↓","WEST":"←"}
        agFace =FACE[abState[DIRECTION]]

        displayList[abState[POINT_Y]][abState[POINT_X]] = agFace


        #迷路を出力する
        print("<<<" + str(titel) +">>>")
        delimiter= ""
        for row  in displayList:
            print(delimiter.join(row))
        print()
    #-------------------------------------------------------------------------------
    def getJudge(self,state):
        """ 迷路判定
        """

        #絶対情報に変換
        abState = self._chgRelativeToAbsolute(state)

        #壁チェック
        if self.mazeList[abState[POINT_Y]][abState[POINT_X]] != "　":
            return "NG"

        #ゴールチェック
        if (self.GAOL[POINT_Y] == abState[POINT_Y]
            and self.GAOL[POINT_X] == abState[POINT_X]):
            return "OK"

        #次の移動
        return "Next"

    #-------------------------------------------------------------------------------
    def _chgRelativeToAbsolute(self,state):
        """ エージェントの相対情報を地図の絶対情報に変換する

            stateはエージェントの開始状態からの相対情報なので
            「START：開始位置」と「FACE ：開始時のエージェントの向き」を用いて絶対情報に変換する

        """


        #相対位置を絶対位置に変換
        if self.FACE == "NORTH":
            stateX = state[POINT_X]
            stateY = state[POINT_Y]
        elif self.FACE == "EAST":
            stateX = -state[POINT_Y]
            stateY = state[POINT_X]
        elif self.FACE == "SOUTH":
            stateX = state[POINT_X]
            stateY = - state[POINT_Y]
        elif self.FACE == "WEST":
            stateX =  state[POINT_Y]
            stateY = state[POINT_X]

        absoluteState=[0,0,""]
        absoluteState[POINT_X] = self.START[POINT_X] + stateX
        absoluteState[POINT_Y]= self.START[POINT_Y] + stateY


        #相対方向を絶対方向に変換
        ABSOLUTE_DIRECTION = ("NORTH","EAST","SOUTH","WEST")#絶対方向
        startIdx = ABSOLUTE_DIRECTION.index(self.FACE)
        relIdx = RELATIVE_DIRECTION.index(state[DIRECTION])
        abIdx = ((startIdx + relIdx)%len(ABSOLUTE_DIRECTION))

        absoluteState[DIRECTION] = ABSOLUTE_DIRECTION[abIdx]


        return absoluteState

#*******************************************************************************
class actionValueFunction(object):
    """ 行動価値関数クラス
    """
    #-------------------------------------------------------------------------------
    def __init__(self):
        #行動-価値辞書
        self.valueDict={}
    #-------------------------------------------------------------------------------
    def __str__(self):
        return str(self.valueDict)
    #-------------------------------------------------------------------------------
    def dump(self):
        """ 行動価値情報の出力
        """
        for key in sorted(self.valueDict.keys()):
            print("%s:%f" % (key,self.valueDict[key]))

    #-------------------------------------------------------------------------------
    def _getKye(self,state,action):
        """ key値作成
        """
        key= copy.deepcopy(state)
        key.append(action)
        return str(key)
    #-------------------------------------------------------------------------------
    def getValue(self,state,action):
        """ 価値を取得
        """
        #key値作成
        key = self._getKye(state,action)

        #行動-価値辞書に存在しない場合は登録
        if not key in self.valueDict:
            self.valueDict[key]  = 0.0

        #価値を戻す
        return self.valueDict[key]
    #-------------------------------------------------------------------------------
    def setValue(self,state,action,Value):
        """ 価値を設定
        """
        #key値作成
        key = self._getKye(state,action)

        #価値を設定
        self.valueDict[key]  = Value
    #-------------------------------------------------------------------------------
    def getMaxValue(self,state):
        """ 同一状態内の最大の価値を取得
        """
        maxValue = 0.0

        #取り得る行動分ループ
        for action in ACTIO:
            #key値作成
            key = self._getKye(state,action)

            #行動-価値辞書に存在する場合チェック
            if key in self.valueDict:
                value = self.valueDict[key]
                if maxValue < value:
                    maxValue = value

        return maxValue
    #-------------------------------------------------------------------------------
    def getGreedy(self,state):
        """ Greedy法による価値取得
        """
        actionList =[]
        maxValue = -2147483648.0

        #取り得る行動分ループ
        for action in ACTIO:

            #key値作成
            key = self._getKye(state,action)

            value = 0.0
            #行動-価値辞書に存在する場合チェック
            if   key in self.valueDict:
                value = self.valueDict[key]

            if maxValue < value:
                actionList = [action]
                maxValue = value
            elif maxValue == value:
                actionList.append(action)

        #複数ある場合は行動をランダムに選択する
        return random.choice(actionList)

#*******************************************************************************
class Agent(object):
    """ エージェントクラス
        エージェントは相対位置[0,0]と相対方向を持っている
        ステータスは相対位置+相対方向で初期状態は[0,0,"FRONT"]とする
    """

    LEARNING_RATE =0.2      #学習係数
    DISCOUNT_FACTOR = 0.9   #割引率
    EPSILON =0.2            #ε-greedy選択の確率
    #-------------------------------------------------------------------------------
    def __init__(self,mazeInfo,quality):
        #迷路情報
        self.mazeInfo = mazeInfo
        #行動価値関数
        self.quality = quality
        #相対位置と相対方向
        self.state_t0 = None
        #時間
        self.time = 0
        #位置・時間リセット
        self._reset()
    #-------------------------------------------------------------------------------
    def _reset(self):
        """位置・時間リセット
        """
        self.state_t0 = [0,0,RELATIVE_DIRECTION[0]]
        self.time = 0
    #-------------------------------------------------------------------------------
    def _nextState(self,action):
        """次の状態を取得
        """
        nextState = copy.deepcopy(self.state_t0)

        if action== "FORWARD_MARCH" or action== "BACKWARD_MARCH":
            #移動の場合
            march = ( 1 if action== "FORWARD_MARCH" else -1)

            if self.state_t0[DIRECTION]=="FRONT":
                nextState[POINT_Y] = self.state_t0[POINT_Y] - 1 * march
            elif self.state_t0[DIRECTION]=="RIGHT":
                nextState[POINT_X] = self.state_t0[POINT_X] - 1 * march
            elif self.state_t0[DIRECTION]=="BACK":
                nextState[POINT_Y] = self.state_t0[POINT_Y] + 1 * march
            elif self.state_t0[DIRECTION]=="LEFT":
                nextState[POINT_X] = self.state_t0[POINT_X] + 1 * march

        elif action== "RIGHT_FACE" or action== "LEFT_FACE":
            #方向転換の場合
            turnT0Idx = RELATIVE_DIRECTION.index(self.state_t0[DIRECTION])
            addIdx = (1 if action== "RIGHT_FACE" else -1)
            turnT1Idx = ((turnT0Idx + addIdx)%len(RELATIVE_DIRECTION))

            nextState[DIRECTION] = RELATIVE_DIRECTION[turnT1Idx]

        return nextState
    #-------------------------------------------------------------------------------
    def _action(self,mode):
        """1行動処理
        """
        #本番の場合は価値で行動
        if mode == "study":
            epsilon = self.EPSILON
        else:
            epsilon = -1.0

        #時刻tで取り得る行動tを決定
        if epsilon > random.random():
            #ランダムに行動選択
            action_t0 = random.choice(ACTIO)
        else:
            # greedy法を適用する
            action_t0 = self.quality.getGreedy(self.state_t0)


        #状態t+1を取得
        state_t1 = self._nextState(action_t0)

        #報酬t+1を取得
        #迷路情報より報酬設定
        judge = self.mazeInfo.getJudge(state_t1)
        if judge == "OK":
             reward_t1  = 10.0
        elif judge == "NG":
             reward_t1  = -1.0
        else:
             reward_t1 = 0.0

        #状態t+1でも最も高い行動価値取得
        maxActionValue_t1= self.quality.getMaxValue(state_t1)

        #時刻tでの行動価値t(状態t,行動t)を取得
        actionValue_t0 = self.quality.getValue(self.state_t0,action_t0)

        #Q値更新
        actionValue_t0 = (actionValue_t0
                            + self.LEARNING_RATE * (reward_t1 + self.DISCOUNT_FACTOR * maxActionValue_t1 - actionValue_t0))
        self.quality.setValue(self.state_t0,action_t0,actionValue_t0)


        #相対位置の設定
        self.state_t0 =  copy.deepcopy(state_t1)
        self.time = self.time + 1

        if mode != "study":
            titel = "TIME = %d, ACTIO = %s" % (self.time,action_t0)
            self.mazeInfo.display(titel,self.state_t0)

        if judge == "Next":
            return False
        else:
            return True
    #-------------------------------------------------------------------------------
    def seriesOfActions(self,mode = "study"):
        """指定された回数行動
        """
        self._reset()

        while True:
            if self._action(mode):
                break

#-------------------------------------------------------------------------------


def main():
    #迷路
    mazeInfo = MazeInfo()
    mazeInfo.display("initial")

    #行動価値関数
    quality = actionValueFunction()

    #エージェント
    agent = Agent(mazeInfo,quality)

    #学習
    for i in range(1000):
        agent.seriesOfActions("study")

    #本番
    agent.seriesOfActions("real")

    #行動価値出力
    print("<<<action Value>>>")
    agent.quality.dump()

if __name__ == '__main__':
    main()