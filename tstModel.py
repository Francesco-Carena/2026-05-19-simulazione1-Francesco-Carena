from model.model import Model

model=Model()
model.createGraph(1)
nodi, archi, artista, influenza=model.getInfoGraph()
print(f"il grafo ha {nodi} nodi, {archi} archi e {artista} è il più influente con {influenza} influenza")

percorso= model.cercaPercorso(90)
print(percorso)
