def x2fs(X, type='purely quadratic'):
    if type == 'interaction':
        s2 = lambda x: x+1
        e2 = lambda x,y : y
    elif type == 'quadratic':
        s2 = lambda x: x
        e2 = lambda x,y: y
    elif type == 'purely quadratic':
        s2 = lambda x: x
        e2 = lambda x,y: x+1
    print type
    l1 = len(X[0])
    l2 = len(X[0])
    for i in range(len(X)):
        r = X[i]
        for j1 in range(l1):
            for j2 in range(s2(j1), e2(j1, l2)):
                print (j1, j2)
                r.append(r[j1]*r[j2])
                
x = [[1,10,100],[2,20,200]];
x2fs(x)
print x