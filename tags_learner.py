import re

def get_blacklist(only_single=False):
    """
    only_single (bool) :weather return only single tags or also double tags \n
    
    """
    singles,doubles=[],[]
    
    with open("tag_conds.csv","r") as f:
        readline=f.readline()
        
        while(readline!=""):
            splited_readline=readline.split(",")
            
            if(splited_readline[1][0]=="1"):
                singles.append(splited_readline[0])
            
            else:
                doubles.append(splited_readline[0])
                
            readline=f.readline()
    
    if(only_single):
        return singles
    return singles,doubles

def learn_blacklist(xml):
    
    singles,doubles=get_blacklist()
    singles,doubles=set(singles),set(doubles)
    
    #<script>./\.</script>,<!.*?>の除外
    pat_script,pat_comment=r'<script.*?>.*?</script.*?>',r'<!--.*?-->'
    xml=re.sub(pat_script,"",xml,flags=re.S)
    xml=re.sub(pat_comment,"",xml,flags=re.S)
    
    pat_starttag=r'<(.*?)>'
    unknowns,ends=set(),set()
    for w in re.findall(pat_starttag,xml,re.S):
        tag=w.split(" ")[0]
        if(tag[0]=="/"):
            ends.add(tag[1:])
        else:
            unknowns.add(tag)
    doubles=doubles|(unknowns&ends)
    unknowns-=doubles|singles
    
    for w in unknowns:
        print("unknown",w)
        pattern=r'<{}.*?>'.format(w)
        match=re.search(pattern,xml,flags=re.S)
        print(xml[match.span()[0]:match.span()[1]+100])
        
        c,check=1,True
        while(check):
            get=input("how about {}\nif tag is Single, enter 1\n enter more to display more strings\n".format(w))
            if(get=="1"):
                singles.add(w.replace("\n",""))
                check=False
            elif(get=="more"):
                c+=1
                print(xml[match.span()[0]:match.span()[1]+100*c])
            elif(get=="unknown"):
                check=False
            elif(get=="0"):
                doubles.add(w.replace("\n",""))
                check=False
    lists=[]
    for w in singles:
        lists.append([w,"1"])
    for w in doubles:
        lists.append([w,"0"])
        
    with open("tag_conds.csv","w") as f:
        for w in range(len(lists)):
            written=",".join(lists[w])+"\n" if(w!=len(lists)-1) else ",".join(lists[w])
            f.write(written)
            """if(w==len(lists)-1):
                f.write(",".join(lists[w]))
            else:
                f.write((",".join(lists[w])+"\n"))"""