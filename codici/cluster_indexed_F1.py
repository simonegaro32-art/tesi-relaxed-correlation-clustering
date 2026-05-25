import gurobipy as gp
from gurobipy import GRB
from instances import instance_cluster_indexed

V, K, A_pos, A_neg, w = instance_cluster_indexed("random_instances_rcc/70_330.g",9)

#Insieme di archi
A = A_pos | A_neg

#Modello
m= gp.Model("cluster_indexed_F1")

#variabili
x = m.addVars(V, K, vtype=GRB.BINARY, name="x")       #x[i,p] = 1 se il vertice i è assegnato al cluster p
t = m.addVars(list(A), vtype=GRB.BINARY, name="t")    #t[i,j] = 1 se l'arco (i,j) viene penalizzato
s = m.addVars(K, K, vtype=GRB.BINARY, name="s")       #s[p,q] = 1 se tra i cluster p e q si penalizzano gli archi positivi, 0 se si penalizzano gli archi negativi

#funzione obiettivo
funObj=0
for (i,j) in A:
    funObj += w[i,j] * t[i,j]
m.setObjective(funObj, GRB.MINIMIZE) 

#vincoli

#(5)
for i in V:
    somma_cluster=0
    for p in K:
        somma_cluster += x[i,p]
    m.addConstr(somma_cluster == 1, name=f"assegnato_{i}")

#(6)
for(i,j) in A_pos:
    for p in K:
        for q in K:
            m.addConstr(
                t[i,j]>=x[i,p] + x[j,q] - 2 + s[p,q]
            )
#(7)
for(i,j) in A_neg:
    for p in K:
        for q in K:
            m.addConstr(t[i,j]>=x[i,p] + x[j,q] - 2 +(1 - s[p,q]))

#(11)
V_sorted = sorted(V)

for i in V_sorted:
    for p in K:

        latoSinistro = 0
        for l in K:
            if l <= p:
                latoSinistro += x[i, l]

        latoDestro = 0
        for j in V_sorted:
            if j < i:
                for l in K:
                    if l <= p - 1:
                        latoDestro += x[j, l]

        latoDestro = latoDestro - (i - 2)

        m.addConstr(latoSinistro >= latoDestro, name=f"sym_{i}_{p}")

#m.write("cluster_indexed.lp")

m.setParam("TimeLimit", 600)
m.optimize()
#Stampa risultati
clusters = {}
for p in K:
    clusters[p] = []

for i in V_sorted:
    for p in K:
        if x[i, p].X > 0.5:
            clusters[p].append(i)
            break
print("\nClusters:")
for p in K:
    print(f"  Cluster {p}: {clusters[p]}")


print("\nArchi penalizzati (t=1):")
for (i,j) in sorted(A):
    if t[i,j].X > 0.5:
        print((i,j), "segno: ", ("+" if (i,j) in A_pos else "-"))
import os
os.system("afplay /System/Library/Sounds/Glass.aiff")