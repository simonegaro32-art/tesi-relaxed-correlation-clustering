import gurobipy as gp
from gurobipy import GRB
from instances import instance_cluster_indexed

V, K, A_pos, A_neg, w = instance_cluster_indexed("random_instances_rcc/70_330.g",9)

#Insieme di archi
A = A_pos | A_neg

#Modello
m= gp.Model("cluster_indexed_F1")

#variabili
x = m.addVars(V, K, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="x")  # x[i,p] continua in [0,1]
t = m.addVars(list(A), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="t")  # t[i,j] continua in [0,1]
s = m.addVars(K, K, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="s")  # s[p,q] continua in [0,1]
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
print("\nArchi penalizzati (t=1):")
for (i,j) in sorted(A):
    if t[i,j].X > 0.5:
        print((i,j), "segno: ", ("+" if (i,j) in A_pos else "-"))


# Lista delle x[i,p] in ordine decrescente di valore
xip_ordinate = sorted(
    [(i, p, x[i, p].X) for i in V_sorted for p in K],
    key=lambda elem: elem[2],
    reverse=True
)
print("\nValori di x[i,p] in ordine decrescente:")
for i, p, val in xip_ordinate:
    print(f"x[{i},{p}] = {val}")

 # Punto 2: scelta di una percentuale di vertici da fissare
percentuale = 0.20   # ad esempio 20%AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
num_vertici_da_fissare = int(percentuale * len(V))

vertici_gia_scelti = set()
vertici_fissati = []

for i, p, val in xip_ordinate:
    if i not in vertici_gia_scelti:
        vertici_fissati.append((i, p, val))
        vertici_gia_scelti.add(i)

    if len(vertici_fissati) == num_vertici_da_fissare:
        break

print(f"\nPercentuale scelta: {percentuale*100:.0f}%")
print(f"Numero di vertici fissati: {len(vertici_fissati)}")

print("\nVertici scelti e cluster assegnato:")
for i, p, val in vertici_fissati:
    print(f"vertice {i} -> cluster {p}   (x[{i},{p}] = {val})")

print("\nVincoli da copiare nel modello F1 ridotto:")
for i, p, val in vertici_fissati:
    print(f'm.addConstr(x[{i},{p}] == 1, name="fix_{i}_{p}")')
