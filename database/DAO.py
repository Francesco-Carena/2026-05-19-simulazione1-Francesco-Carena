from database.DB_connect import DBConnect
from model.artist import Artist
from model.genere import Genere


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getAllGeneri():
        conn=DBConnect.get_connection()
        result=[]
        cursor=conn.cursor(dictionary=True)
        query="""SELECT *
        FROM genre"""

        cursor.execute(query)

        for row in cursor:
            result.append(Genere(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getNodes(genreId):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select DISTINCT ar.ArtistId, ar.Name 
                from track t, album a, artist ar
                where t.GenreId=%s and t.AlbumId=a.AlbumId and ar.ArtistId=a.ArtistId """

        cursor.execute(query, (genreId,))

        for row in cursor:
            result.append(Artist(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getPopularity(genreId):
        conn = DBConnect.get_connection()
        result = {}
        cursor = conn.cursor(dictionary=True)
        query = """select distinct a.ArtistId, SUM(il.Quantity) as Popularity
                    from track t, album a,invoiceline il 
                    where t.AlbumId=a.AlbumId and t.TrackId =il.TrackId and t.GenreId=%s 
                    group by a.ArtistId """

        cursor.execute(query, (genreId,))

        for row in cursor:
            result[row["ArtistId"]]=row["Popularity"]

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges(genreId):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT t1.ArtistId as ID1, t2.ArtistId as ID2
                    FROM (select al.ArtistId , inv.CustomerId 
                    from album al, track t, invoice inv, invoiceline il
                    where al.AlbumId =t.AlbumId  and t.TrackId =il.TrackId and inv.InvoiceId =il.InvoiceId
                    and t.GenreId =%s) t1,
                    (select al.ArtistId , inv.CustomerId 
                    from album al, track t, invoice inv, invoiceline il
                    where al.AlbumId =t.AlbumId  and t.TrackId =il.TrackId and inv.InvoiceId =il.InvoiceId
                    and t.GenreId =%s) t2
                    where t1.customerid =t2.customerid and t1.artistid <t2.artistid """

        cursor.execute(query, (genreId, genreId))

        for row in cursor:
            result.append((row["ID1"], row["ID2"]))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdgesSlow(genreId):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT ar1.ArtistId as ID1, ar2.ArtistId as ID2
                FROM artist ar1, album al1, track t1, invoice inv1, invoiceline il1,
                artist ar2, album al2, track t2, invoice inv2, invoiceline il2
                WHERE 
                inv1.InvoiceId = il1.InvoiceId 
                AND il1.TrackId = t1.TrackId 
                AND t1.AlbumId = al1.AlbumId 
                AND al1.ArtistId = ar1.ArtistId
                
                AND inv2.InvoiceId = il2.InvoiceId 
                AND il2.TrackId = t2.TrackId 
                AND t2.AlbumId = al2.AlbumId 
                AND al2.ArtistId = ar2.ArtistId 
                
                AND inv1.CustomerId = inv2.CustomerId 
                AND ar1.ArtistId < ar2.ArtistId
                
                AND t1.GenreId = %s 
                AND t2.GenreId = %s"""

        cursor.execute(query, (genreId, genreId))

        for row in cursor:
            result.append((row["ID1"],row["ID2"]))

        cursor.close()
        conn.close()
        return result


"""
vertice=Track, arco se due brani nella stessa playlist. Peso = numero di playlist che condividono.
SELECT pt1.TrackId AS id_brano1, pt2.TrackId AS id_brano2, COUNT(pt1.PlaylistId) as playlist_in_comune
FROM playlisttrack pt1, playlisttrack pt2
WHERE pt1.PlaylistId = pt2.PlaylistId
  AND pt1.TrackId < pt2.TrackId
GROUP BY pt1.TrackId, pt2.TrackId;

Nodi=Customer, arco se hanno acquistato lo stesso brano. Peso=numero di brani distinti comprati in comune.
SELECT i1.CustomerId AS id_cliente1, i2.CustomerId AS id_cliente2, COUNT(DISTINCT il1.TrackId) AS brani_comuni
FROM invoice i1
JOIN invoiceline il1 ON i1.InvoiceId = il1.InvoiceId
JOIN invoiceline il2 ON il1.TrackId = il2.TrackId
JOIN invoice i2 ON il2.InvoiceId = i2.InvoiceId
WHERE i1.CustomerId < i2.CustomerId
GROUP BY i1.CustomerId, i2.CustomerId;

Nodi=Employee. Arco orientato va dal "Capo" al "Sottoposto".
SELECT e1.EmployeeId AS id_capo, e2.EmployeeId AS id_sottoposto
FROM employee e1
JOIN employee e2 ON e1.EmployeeId = e2.ReportsTo;

Estrarre solo i clienti che hanno speso complessivamente più di $X
SELECT c.CustomerId, c.FirstName, c.LastName, SUM(i.Total) as SpesaTotale
FROM customer c
JOIN invoice i ON c.CustomerId = i.CustomerId
GROUP BY c.CustomerId
HAVING SUM(i.Total) > %s;

Nodi = Brani che sono stati venduti in quantità maggiore o uguale a N.
SELECT t.TrackId, t.Name, SUM(il.Quantity) as CopieVendute
FROM track t
JOIN invoiceline il ON t.TrackId = il.TrackId
GROUP BY t.TrackId
HAVING SUM(il.Quantity) >= %s;

Artisti che hanno brani di almeno x generi diversi.
SELECT a.ArtistId, a.Name, COUNT(DISTINCT t.GenreId) as NumGeneri
FROM artist a
JOIN album al ON a.ArtistId = al.ArtistId
JOIN track t ON al.AlbumId = t.AlbumId
GROUP BY a.ArtistId
HAVING COUNT(DISTINCT t.GenreId) >= %s;

Playlist sono collegate se condividono almeno N brani. Peso è il costo totale dei brani condivisi.
SELECT pt1.PlaylistId AS id1, pt2.PlaylistId AS id2, SUM(t.UnitPrice) AS peso_arco
FROM playlisttrack pt1
JOIN playlisttrack pt2 ON pt1.TrackId = pt2.TrackId
JOIN track t ON pt1.TrackId = t.TrackId
WHERE pt1.PlaylistId < pt2.PlaylistId
GROUP BY pt1.PlaylistId, pt2.PlaylistId
HAVING COUNT(pt1.TrackId) >= %s;

Nodi: Customer. Archi: Due clienti se hanno acquistato almeno uno stesso brano identico.
Peso: Numero totale di brani distinti acquistati in comune.
SELECT i1.CustomerId AS C1, i2.CustomerId AS C2, COUNT(DISTINCT il1.TrackId) as Peso
FROM invoice i1
JOIN invoiceline il1 ON i1.InvoiceId = il1.InvoiceId
JOIN invoiceline il2 ON il1.TrackId = il2.TrackId
JOIN invoice i2 ON il2.InvoiceId = i2.InvoiceId
WHERE i1.CustomerId < i2.CustomerId
GROUP BY i1.CustomerId, i2.CustomerId;


Nodo=Track di un Genere. Archi: Due brani sono collegati se sono stati acquistati insieme all'interno della stessa fattura/scontrino.
Peso: Numero di fatture in cui i due brani compaiono insieme.
SELECT il1.TrackId AS T1, il2.TrackId AS T2, COUNT(il1.InvoiceId) AS Peso
FROM invoiceline il1
JOIN track t1 ON il1.TrackId = t1.TrackId
JOIN invoiceline il2 ON il1.InvoiceId = il2.InvoiceId
JOIN track t2 ON il2.TrackId = t2.TrackId
WHERE il1.TrackId < il2.TrackId
  AND t1.GenreId = %s AND t2.GenreId = %s
GROUP BY il1.TrackId, il2.TrackId;

Nodi=Artist. Archi: Due artisti sono collegati se hanno almeno un brano all'interno della stessa playlist.
Peso: Numero di playlist distinte in cui compaiono entrambi.
SELECT t1.ArtistId AS id_artista1, t2.ArtistId AS id_artista2, COUNT(DISTINCT t1.PlaylistId) AS peso
FROM (SELECT DISTINCT al.ArtistId, pt.PlaylistId
      FROM album al, track t, playlisttrack pt
      WHERE al.AlbumId = t.AlbumId AND t.TrackId = pt.TrackId) t1,
     (SELECT DISTINCT al.ArtistId, pt.PlaylistId
      FROM album al, track t, playlisttrack pt
      WHERE al.AlbumId = t.AlbumId AND t.TrackId = pt.TrackId) t2
WHERE t1.PlaylistId = t2.PlaylistId
  AND t1.ArtistId < t2.ArtistId
GROUP BY t1.ArtistId, t2.ArtistId;

Nodi=Customer. Archi: Due clienti sono collegati se risiedono nello stesso state e hanno comprato almeno un brano in comune.
Peso: Numero di brani distinti acquistati da entrambi.
SELECT t1.CustomerId AS id1, t2.CustomerId AS id2, COUNT(DISTINCT t1.TrackId) AS brani_condivisi
FROM (SELECT c.CustomerId, c.State, il.TrackId
      FROM customer c, invoice i, invoiceline il
      WHERE c.CustomerId = i.CustomerId AND i.InvoiceId = il.InvoiceId) t1,
     (SELECT c.CustomerId, c.State, il.TrackId
      FROM customer c, invoice i, invoiceline il
      WHERE c.CustomerId = i.CustomerId AND i.InvoiceId = il.InvoiceId) t2
WHERE t1.State = t2.State
  AND t1.TrackId = t2.TrackId
  AND t1.CustomerId < t2.CustomerId
GROUP BY t1.CustomerId, t2.CustomerId;

Nodi=Genre. Archi: Due generi musicali sono collegati se brani di entrambi i generi sono stati acquistati dallo stesso cliente.
Peso: Numero di clienti distinti che hanno comprato entrambi i generi.
SELECT t1.GenreId AS id_genere1, t2.GenreId AS id_genere2, COUNT(DISTINCT t1.CustomerId) AS peso_clienti
FROM (SELECT DISTINCT t.GenreId, i.CustomerId
      FROM track t, invoiceline il, invoice i
      WHERE t.TrackId = il.TrackId AND il.InvoiceId = i.InvoiceId) t1,
     (SELECT DISTINCT t.GenreId, i.CustomerId
      FROM track t, invoiceline il, invoice i
      WHERE t.TrackId = il.TrackId AND il.InvoiceId = i.InvoiceId) t2
WHERE t1.CustomerId = t2.CustomerId
  AND t1.GenreId < t2.GenreId
GROUP BY t1.GenreId, t2.GenreId;

Nodi=Track. Archi: Due brani sono collegati se appartengono allo stesso Album.
Peso: Differenza assoluta in millisecondi tra le durate dei due brani (utile per grafi dove si cerca la distanza/somiglianza).
SELECT t1.TrackId AS id1, t2.TrackId AS id2, ABS(t1.Milliseconds - t2.Milliseconds) AS differenza_durata
FROM track t1, track t2
WHERE t1.AlbumId = t2.AlbumId
  AND t1.TrackId < t2.TrackId;
  
Nodi=Employee e Customer (Grafo Bipartito). Arco: Va dall'agente di supporto (SupportRepId) al cliente che gestisce.
Peso: Il totale in dollari fatturato da quel cliente sotto la gestione di quell'impiegato.
SELECT e.EmployeeId AS id_impiegato, c.CustomerId AS id_cliente, SUM(i.Total) AS fatturato_generato
FROM employee e, customer c, invoice i
WHERE e.EmployeeId = c.SupportRepId
  AND c.CustomerId = i.CustomerId
GROUP BY e.EmployeeId, c.CustomerId;

Nodi=Track. Archi: Due brani sono collegati se sono stati acquistati a meno di X giorni di distanza l'uno dall'altro.
Peso: Il numero di volte in cui questa "vicinanza" di acquisto si è verificata tra i due brani.
SELECT t1.TrackId AS id1, t2.TrackId AS id2, COUNT(*) AS peso
FROM (SELECT il.TrackId, i.InvoiceDate
      FROM invoiceline il, invoice i
      WHERE il.InvoiceId = i.InvoiceId) t1,
     (SELECT il.TrackId, i.InvoiceDate
      FROM invoiceline il, invoice i
      WHERE il.InvoiceId = i.InvoiceId) t2
WHERE t1.TrackId < t2.TrackId
  AND ABS(DATEDIFF(t1.InvoiceDate, t2.InvoiceDate)) < %s
GROUP BY t1.TrackId, t2.TrackId;


SELECT t1.TrackId AS id1, t2.TrackId AS id2, COUNT(*) AS peso
FROM (SELECT il.TrackId, i.InvoiceDate, t.AlbumId
      FROM invoiceline il, invoice i, track t
      WHERE il.InvoiceId = i.InvoiceId 
        AND il.TrackId = t.TrackId) t1,
     (SELECT il.TrackId, i.InvoiceDate, t.AlbumId
      FROM invoiceline il, invoice i, track t
      WHERE il.InvoiceId = i.InvoiceId 
        AND il.TrackId = t.TrackId) t2
WHERE t1.TrackId < t2.TrackId
  AND ABS(DATEDIFF(t1.InvoiceDate, t2.InvoiceDate)) < %s
  AND t1.AlbumId <> t2.AlbumId
GROUP BY t1.TrackId, t2.TrackId;
"""