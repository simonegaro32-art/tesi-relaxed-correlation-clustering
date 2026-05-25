def instance_cluster_indexed(filepath,a):
    K=list(range(1,a+1))
    V=[]
    A_pos=set()
    A_neg=set()
    w={}
    with open(filepath, "r") as istanza:
        prima_linea=istanza.readline().split()
        n=int(prima_linea[0])
        V=list(range(1,n+1))

        for riga in istanza:
            campi=riga.split()
            if len(campi) < 3:
                continue
            i=int(campi[0])+1
            j=int(campi[1])+1
            wij=float((campi[2]))
            arco=(i,j)
            if wij>0:
                A_pos.add(arco)
                w[arco]=wij
            elif wij<0:
                A_neg.add(arco)
                w[arco]=-wij
    return V,K ,A_pos, A_neg, w