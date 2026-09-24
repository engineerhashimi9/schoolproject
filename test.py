d = {
    "Alice": 28,
    "Blice": 70,
    "Bob": 35,
    "Charlie": 28,
    "Diana": 41
}
nd={}
l=list(d.values())
l.sort()
v=list(d.keys())
for i in l :
    for j in d :
        if d[j]==i :
            if i  in nd.values() :
                pass
                
            else : 
                nd[j]=i
            del d[j]
            break
print(nd)
