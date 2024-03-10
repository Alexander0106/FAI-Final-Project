from game.players import BasePokerPlayer
import numpy as np

CDF_N=20
CDF_EPS=1/CDF_N

class MyPlayer(BasePokerPlayer):
    def CdfToWinrate(self,chart):
        winrates=[]
        for i in range(2,15):
            for j in range(2,15):
                if i<j:
                    prob=0.00905
                elif i>j:
                    prob=0.00302
                else:
                    prob=0.004525
                winrates.append((chart[i][j],prob))
        winrates.sort(reverse=True)
        ans={}
        ans_avg={}
        cdf=0
        cdf_sum=0
        index=0
        for i in np.arange(0,1+CDF_EPS,CDF_EPS):
            while cdf<=i:
                cdf+=winrates[index][1]
                cdf_sum+=winrates[index][0]*winrates[index][1]
                index+=1
            ans[i]=winrates[index-1][0]
            ans_avg[i]=cdf_sum/cdf
        self.cdf_to_winrate=ans
        self.cdf_to_winrate_avg=ans_avg

    def AllinWinrate(self,self_cdf,oppo_cdf):
        self_winrate=self.cdf_to_winrate_avg[self_cdf]
        oppo_winrate=self.cdf_to_winrate_avg[oppo_cdf]
        self_win=self_winrate*(1-oppo_winrate)
        oppo_win=oppo_winrate*(1-self_winrate)
        return self_win/(self_win+oppo_win)

    def DpValue0(self,dp,i,j,x,y):
        return (1-x)*dp[i+1][j-5]+x*(1-y)*dp[i+1][j+10]+x*y*self.AllinWinrate(x,y)

    def DpValue1(self,dp,i,j,x,y):
        return (1-y)*dp[i+1][j+5]+y*(1-x)*dp[i+1][j-10]+x*y*self.AllinWinrate(x,y)

    def GameWinrate(self):
        x,y={},{}
        dp={}
        for i in range(21):
            x[i],y[i]={},{}
            dp[i]={}
        for i in range(850-10,995+5,5):
            dp[20][i]=0
        dp[20][1000]=0.5
        for i in range(1005,1150+10+5,5):
            dp[20][i]=1
        for i in range(19,-1,-1):
            dp[i][840]=0
            dp[i][845]=0
            for j in range(850,1150+5,5):
                if i%2==1:
                    max_=None
                    max_x,max_y=None,None
                    for ii in np.arange(0,1+CDF_EPS,CDF_EPS):
                        min_=None
                        min_y=None
                        for jj in np.arange(0,1+CDF_EPS,CDF_EPS):
                            if min_==None or self.DpValue0(dp,i,j,ii,jj)<min_:
                                min_=self.DpValue0(dp,i,j,ii,jj)
                                min_y=jj
                        if max_==None or min_>max_:
                            max_=min_
                            max_x,max_y=ii,min_y
                    x[i+1][j]=max_x
                    y[i+1][j]=max_y
                    dp[i][j]=max_
                else:
                    min_=None
                    min_x,min_y=None,None
                    for jj in np.arange(0,1+CDF_EPS,CDF_EPS):
                        max_=None
                        max_x=None
                        for ii in np.arange(0,1+CDF_EPS,CDF_EPS):
                            if max_==None or self.DpValue1(dp,i,j,ii,jj)>max_:
                                max_=self.DpValue1(dp,i,j,ii,jj)
                                max_x=ii
                        if min_==None or max_<min_:
                            min_=max_
                            min_x,min_y=max_x,jj
                    x[i+1][j]=min_x
                    y[i+1][j]=min_y
                    dp[i][j]=min_
            dp[i][1155]=1
            dp[i][1160]=1
            #print("i:",i)
        self.player0_cdf=x
        self.player1_cdf=y
        self.winrate_game=dp

    def WantWinrate(self):
        self.self_money=round(self.self_money/5)*5
        if self.self_money<850:
            self.want_winrate=0
        elif self.self_money>1150:
            self.want_winrate=1
        else:
            if self.index==0:
                self.want_winrate=self.cdf_to_winrate[self.player0_cdf[self.round_count][self.self_money]]
            else:
                self.want_winrate=self.cdf_to_winrate[self.player1_cdf[self.round_count][2000-self.self_money]]
    
    def Format(self,hole_card):
        number={"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"T":10,"J":11,"Q":12,"K":13,"A":14}
        nums=[number[hole_card[0][1]],number[hole_card[1][1]]]
        if hole_card[0][0]==hole_card[1][0]:
            return sorted(nums,reverse=True)
        else:
            return sorted(nums)

    def __init__(self):
        self.winrate_hand=[
                [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                [None,None,0.51,0.35,0.36,0.37,0.37,0.38,0.40,0.42,0.44,0.47,0.50,0.53,0.57],
                [None,None,0.38,0.55,0.38,0.39,0.39,0.40,0.40,0.43,0.45,0.48,0.51,0.54,0.58],
                [None,None,0.39,0.41,0.58,0.41,0.41,0.42,0.42,0.44,0.46,0.49,0.52,0.55,0.59],
                [None,None,0.40,0.42,0.44,0.61,0.43,0.44,0.44,0.46,0.47,0.50,0.53,0.56,0.60],
                [None,None,0.40,0.42,0.44,0.46,0.64,0.45,0.46,0.47,0.49,0.50,0.53,0.56,0.60],
                [None,None,0.40,0.42,0.44,0.46,0.48,0.67,0.48,0.49,0.50,0.52,0.54,0.57,0.61],
                [None,None,0.43,0.43,0.45,0.47,0.49,0.50,0.70,0.51,0.52,0.54,0.56,0.58,0.62],
                [None,None,0.45,0.46,0.46,0.48,0.50,0.51,0.53,0.73,0.54,0.55,0.57,0.60,0.63],
                [None,None,0.47,0.48,0.49,0.49,0.51,0.53,0.54,0.56,0.76,0.57,0.59,0.62,0.65],
                [None,None,0.49,0.50,0.51,0.52,0.53,0.54,0.56,0.57,0.59,0.78,0.60,0.62,0.65],
                [None,None,0.52,0.53,0.54,0.55,0.56,0.56,0.58,0.59,0.61,0.62,0.81,0.63,0.66],
                [None,None,0.55,0.56,0.57,0.58,0.59,0.59,0.60,0.61,0.63,0.64,0.65,0.83,0.67],
                [None,None,0.59,0.60,0.61,0.62,0.62,0.63,0.64,0.64,0.66,0.67,0.67,0.68,0.86]]
        self.CdfToWinrate(self.winrate_hand)
        self.GameWinrate()

    def declare_action(self, valid_actions, hole_card, round_state):
        #print(self.winrate,self.want_winrate)
        want_fold=False
        if self.win:
            want_fold=True
        elif not (self.lose or self.last_round):
            if self.winrate<self.want_winrate:
                want_fold=True
        if want_fold:
            if self.self_out_now<valid_actions[1]["amount"]:
                return "fold",0
            else:
                return "call",valid_actions[1]["amount"]
        else:
            if self.win_line-self.self_money+1<valid_actions[1]["amount"]:
                return "call",valid_actions[1]["amount"]
            else:
                return "raise",min(max(self.win_line-self.self_money+1,valid_actions[2]["amount"]["min"]),valid_actions[2]["amount"]["max"])

    def receive_game_start_message(self, game_info):
        if game_info["seats"][0]["uuid"]==self.uuid:
            self.index=0
            self.blind={0:5,1:10}
        else:
            self.index=1
            self.blind={0:10,1:5}
        self.win=False
        self.lose=False

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.self_out_now=self.blind[round_count%2]
        self.oppo_out_now=15-self.self_out_now
        self.self_out=0
        self.oppo_out=0
        self.self_money=seats[self.index]["stack"]+self.self_out_now
        self.oppo_money=seats[1-self.index]["stack"]+self.oppo_out_now
        if round_count%2==0:
            self.win_line=1000+(20-round_count)//2*15
            self.lose_line=1000-(20-round_count)//2*15
        else:
            if self.index==0:
                self.win_line=1005+(19-round_count)//2*15
                self.lose_line=990-(19-round_count)//2*15
            else:
                self.win_line=1010+(19-round_count)//2*15
                self.lose_line=995-(19-round_count)//2*15
        self.round_count=round_count
        self.hole_card=hole_card
        self.WantWinrate()
        self.last_round=False

    def receive_street_start_message(self, street, round_state):
        if street=="preflop":
            hole_card_temp=self.Format(self.hole_card)
            self.winrate=self.winrate_hand[hole_card_temp[0]][hole_card_temp[1]]
        else:
            self.self_out+=self.self_out_now
            self.oppo_out+=self.oppo_out_now
            self.self_out_now=0
            self.oppo_out_now=0
            self.winrate=0
            if street=="flop":
                for hand in self.hole_card:
                    for card in round_state["community_card"]:
                        if hand[1]==card[1]:
                            self.winrate+=0.6
                if self.hole_card[0][1]==self.hole_card[1][1]:
                    self.winrate+=0.6
            if street=="turn":
                for hand in self.hole_card:
                    for card in round_state["community_card"]:
                        if hand[1]==card[1]:
                            self.winrate+=0.5
                if self.hole_card[0][1]==self.hole_card[1][1]:
                    self.winrate+=0.5
            if street=="river":
                for hand in self.hole_card:
                    for card in round_state["community_card"]:
                        if hand[1]==card[1]:
                            self.winrate+=0.4
                if self.hole_card[0][1]==self.hole_card[1][1]:
                    self.winrate+=0.4
            number_set=set()
            for hand in self.hole_card:
                number_set.add(hand[1])
            for card in round_state["community_card"]:
                number_set.add(card[1])
            if number_set.issuperset({"A","2","3","4","5"}) or\
                    number_set.issuperset({"2","3","4","5","6"}) or\
                    number_set.issuperset({"3","4","5","6","7"}) or\
                    number_set.issuperset({"4","5","6","7","8"}) or\
                    number_set.issuperset({"5","6","7","8","9"}) or\
                    number_set.issuperset({"6","7","8","9","T"}) or\
                    number_set.issuperset({"7","8","9","T","J"}) or\
                    number_set.issuperset({"8","9","T","J","Q"}) or\
                    number_set.issuperset({"9","T","J","Q","K"}) or\
                    number_set.issuperset({"T","J","Q","K","A"}):
                self.winrate+=1
            color_dict={"C":0,"D":0,"H":0,"S":0}
            for hand in self.hole_card:
                color_dict[hand[0]]+=1
            for card in round_state["community_card"]:
                color_dict[card[0]]+=1
            if color_dict["C"]>=5 or color_dict["D"]>=5 or color_dict["H"]>=5 or color_dict["S"]>=5:
                self.winrate+=1

    def receive_game_update_message(self, new_action, round_state):
        if new_action["action"]!="fold":
            if new_action["player_uuid"]==self.uuid:
                self.self_out_now=new_action["amount"]
            else:
                self.oppo_out_now=new_action["amount"]
            if self.self_money+self.oppo_out+self.oppo_out_now>self.win_line and self.self_money-self.self_out-self.self_out_now<self.lose_line:
                self.last_round=True

    def receive_round_result_message(self, winners, hand_info, round_state):
        money=round_state["seats"][self.index]["stack"]
        if money>self.win_line:
            self.win=True
        if money<self.lose_line:
            self.lose=True
        else:
            self.lose=False


def setup_ai():
    return MyPlayer()
