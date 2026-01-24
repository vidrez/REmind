# Readme analisi dei dati

Lo script python necessita 

```
# Python 3.10.x
# pip install mysql-connector-python pandas matplotlib seaborn
```

e di aggiungere a mano i dati di sql (vedi codice)

`BBperchallange.csv`

Resituisce i blocchi visti per challange (anche ripetuti in teoria poi vedremo perche)

`TimePerchallange.csv`

Resituisce il tempo utilizzato per challange

`time_per_challange.csv`

resituisce il tempo utilizzato per ogni funzione

`figura5_trace.csv`

restituisce il "grafico" per fare figura 5 del paper 

### Obbiettivi di analisi

Visto il paper, con questi dati presi possiamo fare del paper

Figura4  - Relazione tra esperienza e tempo di solving

Figura5- Come si muove tra i blocchi un utente nel tempo 

Table2 - Strategia utilizzata (in questo caso si deve vedere a mano o comunque con il grafico di figura5)

Figura6 - Tempo per strategia (anche qui + i dati del tempo per challange)

Table3 - Tempo mediano per funzione (abbiamo il tempo effettivo di ogni utente sulle singole funzioni)

Figura 10 - numero di visite totale dei Basic block v vs tempo utilizzato in tot per ogni challange (abbiamo il numero dei blocchi visitati per challange) ==in teoria ripetuti ma da controllare==

Figura11 - Numeri di blocchi visitati una singola volta (non fatto)

