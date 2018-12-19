import re

def html_IE(sentence,version="IE 9"):
    """条件式に合う場合TRUE(以降の文は非コメントとして読む)"""
    
    predicate = re.search(r'\[if (.*?)\]',sentence)
    pattern = r'\((.*?)\)'
    subpredicates = re.findall(pattern,predicate.group(),re.S)
    
    if(len(subpredicates)==0):#複数条件が存在しないとき
        return bool(predicate.group(),version)
    
    #接続子を取得
    operators=re.findall(r"\)(.*?)\(",sentence,re.S)
    
    if((len(operators)!=0) & (len(operators)!=len(subpredicates)-1)):
        raise NotEqualError(len(operators),len(subpredicates)-1)
    
    result=bool(subpredicates[0],version)
    for w in range(len(subpredicates)-1):
        if("|" in operators[w]):
            result|=bool(subpredicates[w+1],version)
        elif("&" in operators[w]):
            result&=bool(subpredicates[w+1],version)
        else:
             raise Error("unknown operator")
    return result

def bool(subpredicate,version):
    """
    かっこのない最小単位
    ex)cond="lt IE 9"
    (IE 7),(lt IE 9),(!IEMobile),gt,lt
    """
    
    result,standard=True,subpredicate.find("IE")
    if(standard==-1):
        raise Error("no IE")
        
    if((version=="IEMobile")&(not version in subpredicate)):
        result=False
    
    num=re.search(r"[0-9]",subpredicate)
    if(num!=None):
        if("lt" in subpredicate):
            if(int(version[-1])>=int(num.group())):
                result=False
        elif("gt" in subpredicate):
            if(int(version[-1])<=int(num.group())):
                result=False
        if("lte" in subpredicate):
            if(int(version[-1])>int(num.group())):
                result=False
        elif("gte" in subpredicate):
            if(int(version[-1])<int(num.group())):
                result=False
        else:#
            if(version[-1]!=num.group()):
                result=False
    
    if(subpredicate.find("!")!=-1):
        result= not result
    print(subpredicate,":",result)
    return result

class NotEqualError(Exception):
    def __init__(self,value1,value2):
        self.value1=value1
        self.value2=value2
        self.message="NotEqualError :{0} != {1}".format(value1,value2)
        
class Error(Exception):
    def __init__(self,message):
        print(message)