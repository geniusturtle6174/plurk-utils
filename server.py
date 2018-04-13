from plurk_oauth import PlurkAPI, PlurkOAuth # https://github.com/clsung/plurk-oauth
import configparser
import json
import time
from urllib.request import urlopen

def isAsking(cnt_raw):
    cnt_raw_line = cnt_raw.splitlines()
    # Head
    h = 0
    while(cnt_raw_line[h]!='(coin)(coin)(coin)'):
        h += 1
    # Tail
    t = len(cnt_raw_line) - 1
    while(cnt_raw_line[t]!='(coin)(coin)(coin)'):
        t -= 1
    if((t-h+1)==6):
        return h, t
    else:
        return False

def swapRndnum(num):
    return 1 if num==1 else 0

def yin_yang_yao(sum_num, compute_move=False):
    if(compute_move):
        '''
        Yin : sum is 3 or 2
        Yang: sum is 1 or 0
        '''
        return 0 if(sum_num==3 or sum_num==2) else 1
    else:
        '''
        Yin : sum is 0 or 2
        Yang: sum is 1 or 3
        '''
        return 0 if(sum_num==0 or sum_num==2) else 1

def strToBagua(bin_str):
    dict = {
        # 右邊是底
        '000': '地', # 坤六斷
        '001': '雷', # 震仰盂
        '010': '水', # 坎中滿
        '011': '澤', # 兌上缺
        '100': '山', # 艮覆碗
        '101': '火', # 離中虛
        '110': '風', # 巽下斷
        '111': '天', # 乾三連
    }
    return dict[bin_str]

def baguaToHexagram(bagua_str):
    dict = {
        '天天':   '乾', '天地': '否', '天雷': '无妄', '天水':   '訟', '天山':   '遯', '天風':   '姤', '天火': '同人', '天澤':   '履',
        '地天':   '泰', '地地': '坤', '地雷':   '復', '地水':   '師', '地山':   '謙', '地風':   '升', '地火': '明夷', '地澤':   '臨',
        '雷天': '大壯', '雷地': '豫', '雷雷':   '震', '雷水':   '解', '雷山': '小過', '雷風':   '恆', '雷火':   '豐', '雷澤': '歸妹',
        '水天':   '需', '水地': '比', '水雷':   '屯', '水水':   '坎', '水山':   '蹇', '水風':   '井', '水火': '既濟', '水澤':   '節',
        '山天': '大畜', '山地': '剝', '山雷':   '頤', '山水':   '蒙', '山山':   '艮', '山風':   '蠱', '山火':   '賁', '山澤':   '損',
        '風天': '小畜', '風地': '觀', '風雷':   '益', '風水':   '渙', '風山':   '漸', '風風':   '巽', '風火': '家人', '風澤': '中孚',
        '火天': '大有', '火地': '晉', '火雷': '噬嗑', '火水': '未濟', '火山':   '旅', '火風':   '鼎', '火火':   '離', '火澤':   '睽',
        '澤天':   '夬', '澤地': '萃', '澤雷':   '隨', '澤水':   '困', '澤山':   '咸', '澤風': '大過', '澤火':   '革', '澤澤':   '兌'
    }
    return dict[bagua_str]
    
def listToHexagram(input_list):
    input_list_summed = list(map(sum, input_list))
    print('input_list_summed:', input_list_summed)
    up = '{}{}{}'.format(
        yin_yang_yao(input_list_summed[0]),
        yin_yang_yao(input_list_summed[1]),
        yin_yang_yao(input_list_summed[2]),
    )
    down = '{}{}{}'.format(
        yin_yang_yao(input_list_summed[3]),
        yin_yang_yao(input_list_summed[4]),
        yin_yang_yao(input_list_summed[5]),
    )
    print(up, down, strToBagua(up), strToBagua(down))
    this_hexa = baguaToHexagram(strToBagua(up)+strToBagua(down))
    change_to = None
    if(any(y==0 or y==3 for y in input_list_summed)): # 動爻
        up = '{}{}{}'.format(
            yin_yang_yao(input_list_summed[0], compute_move=True),
            yin_yang_yao(input_list_summed[1], compute_move=True),
            yin_yang_yao(input_list_summed[2], compute_move=True),
        )
        down = '{}{}{}'.format(
            yin_yang_yao(input_list_summed[3], compute_move=True),
            yin_yang_yao(input_list_summed[4], compute_move=True),
            yin_yang_yao(input_list_summed[5], compute_move=True),
        )
        change_to = baguaToHexagram(strToBagua(up)+strToBagua(down))
    return this_hexa, change_to

config = configparser.RawConfigParser()
config.read('config.ini')
App_key = config.get('SECRET', 'App_key')
App_secret = config.get('SECRET', 'App_secret')
oauth_token_secret = config.get('SECRET', 'oauth_token_secret')
oauth_token = config.get('SECRET', 'oauth_token')

print('Authorizing...')
plurk = PlurkAPI(App_key, App_secret)
plurk.authorize(oauth_token, oauth_token_secret)

# Do some tests for a certain fixed plurk (https://www.plurk.com/p/mpxyit)
req = plurk.callAPI('/APP/Timeline/getPlurk/?plurk_id={}'.format(1373830661))
content_raw = req['plurk']['content_raw']
content = req['plurk']['content']
is_ask = isAsking(content_raw)
if(is_ask):
    h, t = is_ask
    hexagram_raw = content.split('<br />')[h:t+1]
    hexagram_list = [[swapRndnum(int(y.split(' ')[-2][-2])) for y in c.split('<')[1:]] for c in hexagram_raw ]
    print(listToHexagram(hexagram_list))
    


'''
comet = plurk.callAPI('/APP/Realtime/getUserChannel')
comet_channel_str = comet.get('comet_server') + "&new_offset={}"
new_offset = -1
while True:
    print('Looping...')
    req = urlopen(comet_channel_str.format(new_offset), timeout=20)
    rawdata = req.read()
    print(rawdata)
    data = json.loads(rawdata)
    new_offset = data.get('new_offset', -1)
    msgs = data.get('data')
    if(not msgs):
        #time.sleep(1)
        #continue
        break
    for msg in msgs:
        content_raw = msg.get('content_raw')
        content = msg.get('content')
        if('coin' in content_raw):
            print(msg)
'''