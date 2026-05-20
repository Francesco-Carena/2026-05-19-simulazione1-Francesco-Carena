import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._choiceGenre=None
        self._choiceArtist=None

    def fillDDGenre(self):
        generi=self._model.getAllGeneri()
        for g in generi:
            self._view._ddGenre.options.append(ft.dropdown.Option(data=g, key=str(g.GenreId),text=g.Name))
        self._view.update_page()

    def readDDGenre(self, e):
        self._choiceGenre=int(self._view._ddGenre.value)
        #print(f"Selezionato il genere {self._choiceGenre}")
    def readDDArtist(self, e):
        self._choiceArtist=int(self._view._ddArtist.value)

    def handleCreaGrafo(self, e):
        if self._choiceGenre is None:
            self._view.create_alert("Selezionare prima un genere!")
            self._view.update_page()
            return
        self._view._ddArtist.options.clear()
        self._view.txt_result.clean()
        self._model.createGraph(int(self._choiceGenre))
        topEdges=self._model.getTopEdges()
        nodi, archi, artista, influenza=self._model.getInfoGraph()
        self._view.txt_result.controls.append(ft.Text(f"Grafo correttamente creato"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {nodi}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {archi}"))
        self._view.txt_result.controls.append(ft.Text(f"Artista + influente: {artista} con {influenza} influenza"))
        for e in range(len(topEdges)):
            u,v,dati=topEdges[e]
            self._view.txt_result.controls.append(ft.Text(f"{u} -> {v}: {dati["weight"]}"))
        artisti=self._model.getArtist()
        for a in artisti:
            self._view._ddArtist.options.append(ft.dropdown.Option(data=a, key=a.ArtistId, text=a.Name))
        self._view.update_page()

    def handleCammino(self,e):
        if self._choiceArtist is None:
            self._view.create_alert("Selezionare prima un artista!")
            self._view.update_page()
            return
        self._view.txt_result.clean()
        percorso=self._model.cercaPercorso(self._choiceArtist)
        self._view.txt_result.controls.append(ft.Text(f"percorso trovato:"))
        for artist in percorso:
            self._view.txt_result.controls.append(ft.Text(f"{artist}"))
        self._view.update_page()

