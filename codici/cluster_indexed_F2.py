import gurobipy as gp
from gurobipy import GRB
from instances import instance_cluster_indexed

V, k, A_pos, A_neg, w = instance_cluster_indexed("random_instances_rcc/70_330.g",9)


#Insieme di archi
A = A_pos | A_neg

V_sorted = sorted(V)

#Modello
m = gp.Model("cluster_indexed_F2")

#variabili
x_index = [(i, j) for i in V_sorted for j in V_sorted if i <= j]
x = m.addVars(x_index, vtype=GRB.BINARY, name="x")    #x[i,j] = 1 se il vertice j è rappresentato dal vertice i
t = m.addVars(list(A), vtype=GRB.BINARY, name="t")    #t[i,j] = 1 se l'arco (i,j) viene penalizzato
s = m.addVars(V_sorted, V_sorted, vtype=GRB.BINARY, name="s")   #s[i,j] = 1 se tra i cluster rappresentati da i e j si penalizzano gli archi positivi, 0 se si penalizzano gli archi negativi

#funzione obiettivo
funObj = 0
for (i, j) in A:
    funObj += w[i, j] * t[i, j]
m.setObjective(funObj, GRB.MINIMIZE)

#vincoli

#(12)
for j in V_sorted:
    somma_rappresentanti = 0
    for i in V_sorted:
        if i <= j:
            somma_rappresentanti += x[i, j]
    m.addConstr(somma_rappresentanti == 1, name=f"rappresentato_{j}")

#(13)
for i in V_sorted:
    for j in V_sorted:
        if i < j:
            m.addConstr(x[i, j] <= x[i, i], name=f"attivo_{i}_{j}")

#(14)
somma_representatives = 0
for i in V_sorted:
    somma_representatives += x[i, i]
m.addConstr(somma_representatives <= len(k), name="max_clusters")


#(15)
for (i, j) in A_pos:
    for u in V_sorted:
        if u <= i:
            for v in V_sorted:
                if v <= j:
                    m.addConstr(
                        t[i, j] >= x[u, i] + x[v, j] - 2 + s[u, v]
                    )

#(16)
for (i, j) in A_neg:
    for u in V_sorted:
        if u <= i:
            for v in V_sorted:
                if v <= j:
                    m.addConstr(
                        t[i, j] >= x[u, i] + x[v, j] - 2 + (1 - s[u, v])
                    )

#m.write("cluster_indexed_F2.lp")
m.setParam("TimeLimit", 600)
m.optimize()

#Stampa risultati

representatives = []
for i in V_sorted:
    if x[i, i].X > 0.5:
        representatives.append(i)

clusters = {}
for i in representatives:
    clusters[i] = []

for j in V_sorted:
    for i in V_sorted:
        if i <= j and x[i, j].X > 0.5:
            clusters[i].append(j)
            break

print("\nRepresentatives:")
for i in representatives:
    print(i)

print("\nClusters:")
for i in representatives:
    print(f"  Rep {i}: {clusters[i]}")

print("\nArchi penalizzati (t=1):")
for (i, j) in sorted(A):
    if t[i, j].X > 0.5:
        print((i, j), "segno: ", ("+" if (i, j) in A_pos else "-"))
import os
os.system("afplay /System/Library/Sounds/Glass.aiff")