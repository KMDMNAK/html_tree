import re
from collections import Counter

class node:
    def __init__(self,index0,*attrs):
        self.index=[index0,(0,0)]
        self.list=[]
        self.text=[]
        self.tag=""
        self.parent=None

class tree:
    def __init__(self,xml,Text=True,limit=1):
        self.xml,self.tags,self.blacklist,self.c=xml,[],get_blacklist(True),0
        print("black:",self.blacklist)
        self.Text=Text#textを処理するかどうか
        self.limit=limit#textにlimit以上の文字数のあるnodeを取得する。
        self.textnodes=[]#textがlimitを超えたnodeの格納場所
        self.c=0
        
    def make_tree(self,IE_version='IE 9'):
        """IE_version:条件付きコメントに対する挙動を設定する。\n
        IE_version in {'IE 9','IE 8','IE 7','IE 6'}"""
        index,self.trees=(0,0),[]
        while(index[1]!=len(self.xml)):
            bool,index,node=self.recursive(skip=index[1])
            if(node!=None):
                self.trees.append(node)
    
    def recursive(self,skip=0,parent=None):
        """次タグを見つける操作をrecursiveで行ってしまう。\n
        次のタグを検知.一番最初には<script>等の要除外タグは来ない前提\n
        <! if>は入れ子に対応する必要がある。"""
        
        thisistag,index_t=self.search_tag(skip=skip)
        thisc=self.c
        self.c+=1
        if(thisistag):
            thisnode=self.make_node(index_t,parent)
            if(thisnode.tag=="script"):
                pat=r'</script>'
                last=re.search(pat,self.xml[index_t[1]:],flags=re.S).span()
                last=(last[0]+index_t[1],last[1]+index_t[1])
                index_t,thisnode.index[1]=last,last#当タグの終タグに指定
                print("get_script")
            elif(thisnode.tag[0:3]=='!--'):#コメントの処理
                sentence=self.xml[index_t[0]:index_t[1]]
                if(re.search(r'--\[if.*?]',cond,flags=re.S)!=None):#条件付きコメント
                    if(html_IE(sentence,self.version)):#非コメントとして読む
                        thisnode.index[1]=index_t
                    else:#コメントとして読む
                        pat=r'<![endif]-->'
                        last=re.search(pat,self.xml[index_t[1]:],flags=re.S).span()
                        last=(last[0]+index_t[1],last[1]+index_t[1])
                        index_t,thisnode.index[1]=last,last#当タグの終タグに指定
                        print("get_endif")
                else:
                    thisnode.index[1]=index_t
            elif(thisnode.tag in self.blacklist):
                thisnode.index[1]=index_t
            else:#普通の始タグだった場合
                check=True
                while(check):
                    index_blast=index_t[1]
                    check,index_t,child_node=self.recursive(index_t[1],thisnode)
                    if(check):
                        thisnode.text.append(self.xml[index_blast:child_node.index[0][0]])
                        thisnode.list.append(child_node)
                thisnode.index[1]=index_t
                thisnode.text.append(self.xml[index_blast:index_t[0]])
            if(self.Text):
                thisnode.text=re.sub(r'\t|\n',"","".join(thisnode.text))
                if(len(thisnode.text.replace(" ",""))>=self.limit):
                    self.textnodes.append(thisnode)
        else:#終タグだった場合
            thisnode=None
        if(thisnode!=None):
            if((self.xml[thisnode.index[0][0]+1:thisnode.index[0][1]-1].split(" ")[0]!=self.xml[thisnode.index[1][0]+2:thisnode.index[1][1]-1])):#(thisnode.index[0]!=thisnode.index[1])&
                print(self.xml[thisnode.index[0][0]:thisnode.index[0][1]],(thisnode.index[0][0],thisnode.index[0][1]))
                print(self.xml[thisnode.index[1][0]:thisnode.index[1][1]],(thisnode.index[1][0],thisnode.index[1][1]))
                print()
        
        return thisistag,index_t,thisnode
        
    def search_tag(self,skip):#boolean,taple
        """skip以降最初に現れるタグが終タグか始タグかを判別\n
        True if next tag is not end tag otherwise False \nreturn boolean and index(integer)"""
        pat=r'<.*?>'
        match=re.search(pat,self.xml[skip:],flags=re.S)
        if(match==None):
            #print("match:",match)
            print("skip:",skip)
            return False,(skip,len(self.xml))
        isStart=True
        if(match.group()[1]=="/"):
            isStart=False
        before=match.span()
        return isStart,(before[0]+skip,before[1]+skip)#(int s,int l)
    
    def make_node(self,index0,parent_node):
        """indexは<.*?>の場所を指定(括弧もいれること)"""
        node_=node(index0)
        
        #parentに指定
        node_.parent=parent_node
        
        #タグの中身を分割
        pat=r'<(.*?)>'
        match=self.xml[index0[0]+1:index0[1]-1]
        sps=match.split(" ")
        
        #attributeを取得
        node_.attr=[]
        pat_forat=r'(.+?)=.*?\"(.*?)\"'
        for w in sps[1:]:
            fa=re.findall(pat_forat,w)
            if(len(fa)!=0):
                node_.attr.append(fa[0])#(w.split("="))
        
        #tagを取得
        node_.tag=sps[0]
        if(not node_.tag in self.tags):
            self.tags.append(node_.tag)
        
        return node_
    
    def search_tags(self,*tags,tree_index=0):
        """指定したタグのついた木を取得する。\n
        first:検索する木のindex"""
        wait=[self.trees[tree_index]]
        targets=[wait[0]] if(wait[0].tag in tags) else []
        while(wait!=[]):
            wait_c=[]
            for w in wait:
                for v in w.list:
                    wait_c.append(v)
                    if(v.tag in tags):
                        targets.append(v)
            wait=wait_c
        print("tags",tags)
        return targets
    
    def search_attrs(self):
        pass

def get_blacklist(only_single=False):
    
    singles,doubles=[],[]
    with open("tag_conds.csv","r") as f:
        s=f.readline()
        while(s!=""):
            sp=s.split(",")
            if(sp[1][0]=="1"):
                singles.append(sp[0])
            else:
                doubles.append(sp[0])
            s=f.readline()
    if(only_single):
        return singles
    else:
        return singles,doubles

def learn_blacklist(xml):
    
    singles,doubles=get_blacklist()
    #メモリから情報を抜き出す。
    #lists=singles.copy().extend(doubles)
    unknowns=[]
    singles,doubles=set(singles),set(doubles)
    lists=singles|doubles

    #<script>./\.</script>の除外
    pat_script,pat_ex=r'<script.*?>.*?</script.*?>',r'<!.*?>'
    xml=re.sub(pat_script,"",xml)
    xml=re.sub(pat_ex,"",xml)

    pat_s,starts,ends=r'<(.*?)>',set(),set()
    for w in re.findall(pat_s,xml,flag=re.S):
        tag=w.split(" ")[0]
        if(tag[0]=="/"):
            ends.add(tag)
        else:
            starts.add(tag)

    se=starts&ends
    doubles=doubles|se
    starts-=se|singles

    for w in starts:
        if(lists!=None):
            if(not w in lists):
                unknowns.append(w)
        else:
            unknowns.append(w)

    for w in unknowns:
        print("unknown",w)
        pat=r'<{}.*?>'.format(w)
        mat=re.search(pat,xml,flag=re.S)
        print(xml[mat.span()[0]:mat.span()[1]+100])
        c=1
        check=True

        while(check):
            get=input("how about {}\nif tag is Single, enter 1\n enter more to display more strings\n".format(w))
            if(get=="1"):
                singles.add(w)
                check=False
            elif(get=="more"):
                c+=1
                print(xml[mat.span()[0]:mat.span()[1]+100*c])
            elif(get=="unknown"):
                check=False
            elif(get=="0"):
                doubles.add(w)
                check=False
    lists=[]
    for w in singles:
        lists.append([w,"1"])
    for w in doubles:
        lists.append([w,"0"])

    with open("tag_conds.csv","w") as f:
        for w in range(len(lists)):
            if(w==len(lists)-1):
                f.write(",".join(lists[w]))
            else:
                f.write((",".join(lists[w])+"\n"))
                
def html_IE(sentence,version):
    """条件式に合う場合TRUE(以降の文は非コメントとして読む)"""
    
    cond=re.findall(r'\[if (.*?)\]',sentence)[0]
    pat=r'\((.*?)\)'
    f,c=re.search(pat,cond),0
    if(f!=None):
        
    else:
        while(f!=None):
            f=re.search(pat,cond[f.end])
        if(len(conds)==1):
            return True if(conds[0]==version) else False
        elif(len(conds==2)):
            pass

def bool(cond,version):
    """
    ex)cond="lt IE 9"
    (IE 7),(lt IE 9),(!IEMobile),gt,lt
    """
    result=True
    
    standard=cond.find("IE")
    if(standard==-1):
        print("Error: no IE")
        result=Falses
    if(version=="IEMobile"):
        if(version in cond):
            result=True
    else:
        num=re.findall("[1-9]")
        if(num!=-1):
            
        else:#IEすべてに該当
            result=True
        cond[:standard]
    if(cond.find("!")!=-1):
        return not result
    
def kakko(sen,start_index=0,skip=0):
    pat=r'\(|\)'
    match=re.search(pat,sen[skip:])
    if(match.group()=='('):
        return kakko(sen,match.group())
    elif(match.group()==')'):
        
        return False

import igraph as ig
def make_graph(first_node):
    fr,to=0,0
    wait=[first_node]
    order_tag=[wait[0].tag]
    Edges=[]
    while(wait!=[]):
        wait_c=[]
        for w in wait:
            for v in w.list:
                to+=1
                wait_c.append(v)
                order_tag.append(v.tag)
                Edges.append((fr,to))
            fr+=1
        wait=wait_c
    
    graph=ig.Graph(Edges)
    
    graph.vs["label_dist"],graph.es["arrow_width"],graph.vs["label"]=1.0,1.0,order_tag
    layout=graph.layout("rt",0)
    ig.plot(graph,layout=layout,bbox=(6000,6000))