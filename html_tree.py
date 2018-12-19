import re
#from collections import Counter
import explorer
import tags_learner

class node:
    def __init__(self,first_index,*attrs):
        """
        Args:
            first_index (int two size tuple): index of this node's start tag in given html
        """
        
        self.index=[first_index,(0,0)]
        self.list,self.text=[],[]
        self.tag,self.parent="",None
        self.number,self.lastchild_number=0,0
        
    def check_index(self,html):
        print("start tag:",html[self.index[0][0]:self.index[0][1]])
        print("end tag:",html[self.index[1][0]:self.index[1][1]])
        
class tree:
    
    def __init__(self,xml,Text=True,limit=1):
        """
        
        """
        
        self.xml,self.tags,self.blacklist,self.c=xml,[],tags_learner.get_blacklist(True),0
        print("black:",self.blacklist)
        #whether you want to get texts of html
        self.Text=Text
        self.limit=limit#textにlimit以上の文字数のあるnodeを取得する。
        self.textnodes=[]#textがlimitを超えたnodeの格納場所
        self.c=0
        self.text_number=0
        
    def make_tree(self,IE_version='IE 9'):
        """IE_version:条件付きコメントに対する挙動を設定する。\n
        IE_version in {'IE 9','IE 8','IE 7','IE 6'}"""
        index,self.trees,self.version=(0,0),[],IE_version
        while(index[1]!=len(self.xml)):
            bool,index,node=self.recursive(skip=index[1])
            if(node!=None):
                self.trees.append(node)
        
    def recursive(self,skip=0,parent=None):
        
        """次タグを見つける操作をrecursiveで行う。\n
        次のタグを検知.\n
        一番最初には<script>等の要除外タグは来ない前提\n
        explorer特有のhtmlの挙動を考慮する必要がある."""
        
        thisistag,index_t=self.search_tag(skip=skip)
        
        if(thisistag):
            self.c+=1
            thisnode=self.make_node(index_t,parent)
            thisnode.number=self.c
            
            if(thisnode.tag=="script"):
                pat=r'</script>'
                last=re.search(pat,self.xml[index_t[1]:],flags=re.S).span()
                last=(last[0]+index_t[1],last[1]+index_t[1])
                index_t,thisnode.index[1]=last,last#当タグの終タグに指定
                
            elif(thisnode.tag[0]=='!'):#コメントの処理
                sentence=self.xml[index_t[0]:index_t[1]]
                if(re.search(r'\[if.*?\]',sentence,flags=re.S)!=None):#条件付きコメント
                    if(explorer.html_IE(sentence,self.version)):#非コメントとして読む
                        thisnode.index[1]=index_t
                    else:#コメントとして読む
                        pat=r'<!\[.*?endif.*?\].*?-->'
                        last=re.search(pat,self.xml[index_t[1]:],flags=re.S).span()
                        last=(last[0]+index_t[1],last[1]+index_t[1])
                        index_t,thisnode.index[1]=last,last#当タグの終タグに指定
                        #print("get_endif")
                else:
                    thisnode.index[1]=index_t
                    
            elif(thisnode.tag in self.blacklist):
                thisnode.index[1]=index_t
                
            else:#普通の始タグだった場合
                check=True
                while(check):
                    index_blast=index_t[1]
                    check,index_t,child_node=self.recursive(index_t[1],thisnode)
                    
                    if(child_node!=None):
                        thisnode.list.append(child_node)
                        self.text_number += 1
                        add_text=re.sub(r'\n|\r',"",self.xml[index_blast:child_node.index[0][0]])
                        print(add_text)
                        if(not add_text in ["",'',' ',None]):
                            thisnode.text.append((self.text_number,add_text))
                            
                thisnode.index[1]=index_t
                
                self.text_number += 1
                add_text = re.sub(r'\t|\n|\r',"",self.xml[index_blast:index_t[0]])
                
                if(not add_text in ["",'',' ',None]):
                    thisnode.text.append((self.text_number,add_text))
                    
            thisnode.lastchild_number=self.c
            
            if(self.Text):#textの取得
                #thisnode.text=re.sub(r'\t|\n|\r',"","".join(thisnode.text))
                text=""
                for w in thisnode.text:
                    text+=w[1]
                if(len(text.replace(" ",""))>=self.limit):
                    self.textnodes.append(thisnode)
        else:#終タグだった場合
            thisnode=None
        
        return thisistag,index_t,thisnode
        
    def search_tag(self,skip):#boolean,taple
        """skip以降最初に現れるタグが終タグか始タグかを判別\n
        True if next tag is not end tag otherwise False \n
        return boolean and index(integer)
        """
        
        pat=r'<.*?>'
        match=re.search(pat,self.xml[skip:],flags=re.S)
        if(match==None):
            #print("match:",match)
            print("skip:",skip)
            return False,(skip,len(self.xml))
        
        if(match.group()[1:4]=="!--"):
            if((not "\[if" in match.group())&(not "endif" in match.group())):
                match=re.search(r'<!--.*?-->',self.xml[skip:],flags=re.S)
                print("match:",match)
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
        match=self.xml[index0[0]+1:index0[1]-1].replace("\n","")
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
        """
        指定したタグのついた木を取得する。\n
        first:検索する木のindex
        """
        
        quence=[self.trees[tree_index]]
        targets=[quence[0]] if(quence[0].tag in tags) else []
        while(quence!=[]):
            quence_copy=[]
            for w in quence:
                for v in w.list:
                    quence_copy.append(v)
                    if(v.tag in tags):
                        targets.append(v)
            quence=quence_copy
        print("tags",tags)
        return targets
    
    def search_attrs(self):
        pass
    
    def print_text(self,Sort=True):
        self.text=[]
        
        for w in self.textnodes:
            self.text.extend(w.text)
            
        if(Sort):
            self.text=sorted(self.text, key=lambda x:x[0])
        for w in self.text:
            print(w[1])
            
def conditional_comment():
    """
    check whether explorer version satisfy comment's version \n
    
    """
    pass