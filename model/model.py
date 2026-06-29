import copy

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph=nx.DiGraph()
        self._idMapArtists={}
        self._bestPath=[]
        self._bestObjValue=0

    def createGraph(self, genreId):
        self._graph.clear()
        self._graph.clear_edges()
        self._idMapArtists = {}
        artists=DAO.getNodes(genreId)
        self._graph.add_nodes_from(artists)
        for a in artists:
            self._idMapArtists[a.ArtistId]=a
        self._getPopularity(genreId)
        self._addEdges(genreId)

    def _getPopularity(self,genreId):
        popularity=DAO.getPopularity(genreId)
        for a_id, artista in self._idMapArtists.items():
            artista.popularity=int(popularity.get(a_id,0))


    def _addEdges(self,genreId):
        edges=DAO.getAllEdges(genreId)
        for id1,id2 in edges:
            if id1 in self._idMapArtists and id2 in self._idMapArtists:
                a1=self._idMapArtists[id1]
                a2=self._idMapArtists[id2]
                peso=a1.popularity+a2.popularity

                if a1.popularity>a2.popularity:
                    self._graph.add_edge(a1,a2,weight=peso)
                elif a2.popularity>a1.popularity:
                    self._graph.add_edge(a2,a1,weight=peso)
                else:
                    self._graph.add_edge(a1,a2,weight=peso)
                    self._graph.add_edge(a2,a1,weight=peso)

    def getAllGeneri(self):
        return DAO.getAllGeneri()

    def getInfoGraph(self):
        bestArtist=None
        influenceMax=-float('inf')
        for artist in self._graph.nodes:
            influenza=self._calcolaInfluenza(artist)
            if influenza>influenceMax:
                bestArtist=artist
                influenceMax=influenza
        return len(self._graph.nodes), len(self._graph.edges), bestArtist, influenceMax

    def _calcolaInfluenza(self, artist):
        pesoUscenti=0
        pesoEntranti=0
        for u,v, data in self._graph.out_edges(artist, data=True):
            pesoUscenti+=data["weight"]
        for u,v, data in self._graph.in_edges(artist, data=True):
            pesoEntranti+=data["weight"]
        return pesoUscenti-pesoEntranti

    def getTopEdges(self):
        edges= sorted(self._graph.edges(data=True), key=lambda x: x[2]["weight"], reverse= True)
        return edges[:5]
    def getArtist(self):
        return self._graph.nodes()

    def cercaPercorso(self, artistId):
        source=self._idMapArtists[artistId]
        #self._longestPathCost=0
        self._bestPath=[]
        parziale=[source]
        self._ricorsione(parziale, pesoUltimo=-1)

        return self._longestPath


    def cercaPercorsoV2(self, artistId):
        self._bestPath = []
        #self._bestObjValue = 0

        source = self._idMapArtists[artistId]
        parziale = [source]

        self._ricorsioneV2(parziale)

        return self._bestPath

    def _ricorsioneV2(self, parziale):
        if len(parziale) > self._bestObjValue:
            self._bestPath = copy.deepcopy(parziale)
            self._bestObjValue = len(parziale)

        nodoCorrente = parziale[-1]
        for v in self._graph.neighbors(nodoCorrente):
            if v not in parziale:
                peso_nuovo = self._graph[nodoCorrente][v]["weight"]
                if len(parziale) == 1:
                    peso_valido = True
                else:
                    peso_vecchio = self._graph[parziale[-2]][nodoCorrente]["weight"]
                    peso_valido = peso_nuovo > peso_vecchio

                if peso_valido:
                    parziale.append(v)
                    self._ricorsioneV2(parziale)
                    parziale.pop()



    def _ricorsione(self,parziale, pesoUltimo):
        if len(parziale)>len(self._longestPath):
            self._longestPath=copy.deepcopy(parziale)

        nodoCorrente=parziale[-1]
        for vicino in self._graph.neighbors(nodoCorrente):
            if vicino not in parziale:
                peso_nuovo_arco = self._graph[nodoCorrente][vicino]["weight"]
                if peso_nuovo_arco>pesoUltimo:
                    parziale.append(vicino)
                    self._ricorsione(parziale,peso_nuovo_arco)
                    parziale.pop()