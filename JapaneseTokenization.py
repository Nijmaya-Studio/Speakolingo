s = """*拝啓*時下ますます*ご健勝*のこととお喜び申し上げます。さて、この一年を*振り返り*、*下記*により*忘年会**を開催*いたします。*ご参加*くださいますようお願いいたします#はいけい ごけんしょう ふりかえり ぼうねんかい かいさい さんか"""

def Tokenize(text):
    
    if '#' not in text:
        return [list(text),list(text)]
    
    l = text.split('#')
    l = [l[0].split('*'),l[1].split(' ')]

    l1 = []
    for i in l[0]:
        if i != '':
            l1.append(i)
        else:
            continue

    def fromlist(l:list) -> str:
        s = ''
        for i in l:
            s += i
        return s
    
    val = {}
    for i in range(len(l[1])):
        val[l[0][2*i+1]] = l[1][i]
        
    oldlist = []
    for i in l[0]:
        if i != '':
            oldlist.append(i)

    newlist = []

    for i in oldlist:
        if i in val.keys():
            newlist.append(val[i])
        else:
            newlist.append(i)
            
    return [oldlist, newlist]

Tokenize(s)