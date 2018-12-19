import igraph as ig

def make_graph(root_node):
    
    from,to=0, 0
    queue = [root_node]
    order_tag ,Edges = [queue[0].tag] ,[]
    
    while(queue!=[]):
        next_queue=[]
        for w in queue:
            for v in w.list:
                
                to+=1
                next_queue.append(v)
                order_tag.append(v.tag)
                Edges.append((from,to))
            
            from+=1
        
        queue=next_queue
    
    graph=ig.Graph(Edges)
    graph.vs["label_dist"],graph.es["arrow_width"],graph.vs["label"]=1.0,1.0,order_tag
    layout=graph.layout("rt",0)
    
    ig.plot(graph,layout=layout,bbox=(6000,6000))