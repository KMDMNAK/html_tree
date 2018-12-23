import html_tree as ht

class Learner:
    
    def __init__(self):
        pass
    #,trees):
    #self.trees=trees
    
    def analysis(self,html=None,tree=None):
        if(tree==None):
            if(html==None):
                raise NoHtmlError()
            tree=ht.tree(html)
            tree.make_tree()
            tree.get_text()
        text_numbers=[]
        for w in tree.text:
            text_numbers.append(w[0])
            print("[{}] : ".format(w[0]),w[1])
        original_input=input("indicate number\n>")
        numbers=set(text_numbers)&indicate_number(original_input,max(text_numbers))
        print("numbers:",numbers)
        selected_textnodes=[]
        for w in tree.textnodes:
            check=True
            i=0
            while(check):
                if(w.text[i][0] in numbers):
                    selected_textnodes.append(w)
                    check=False
                i+=1
                if(i>=len(w.text)):
                    check=False
        return selected_textnodes   
import re

def indicate_number(original_input,index_size):
    """split by "," \n
    operator +(1,2,3,last),-(9-11),+(10)
    you can indicate operate through numbers using "-" in () ,ex: +(1-3) equal to +(1,2,3) \n
    you can use some word like "last" ex:
    """
    
    pat=r'(.*?\).*?,?)'
    predicates=re.findall(pat,original_input)
    plus,minus=[],[]
    
    for w in predicates:
        get=re.search(r'\((.*?)\)',w)

        PLUS=True if (w[:get.start()].replace(" ","")=="+")else False
        parts=w[get.start()+1:get.end()-1].replace(" ","")
        print(parts)
        
        for v in parts.split(","):
            v=v.replace("last",str(index_size))
            if(v.find("-")!=-1):
                through=v.split("-")
                for i in range(int(through[0]),int(through[1])+1):
                    if(PLUS):
                        plus.append(i)
                    else:
                        minus.append(i)
            else:
                if(PLUS):
                    plus.append(int(v))
                else:
                    minus.append(int(v))
    result=set(plus)-set(minus)
    return result
class NoHtmlError(Exception):
    def __init__(self):
        print("No Html")