from model.model import Model

model=Model()
model.createGraph(6)
nodi, archi, artista=model.getInfoGraph()
print(f"il grafo ha {nodi} nodi, {archi} archi e {artista} è il più influente")