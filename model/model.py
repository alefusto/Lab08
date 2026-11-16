from database.distributore_DAO import DistributoreDAO
import copy

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        lista_prezzi_medi = []
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi() # Recupero tutti i prezzi del singolo distributore dal DTO
            prezzi_mese = []
            for prezzo in prezzi:
                if prezzo.data.month == mese: # Controllo il mese per ogni prezzo su cui itero; .data.month estrae il mese da un oggetto di classe Data e attributo month
                    prezzi_mese.append(prezzo.prezzo_litro) # prezzo_litro è l'attributo nel DAO
            giorni = len(prezzi_mese)
            if giorni > 0:
                media = float(sum(prezzi_mese)/giorni)
                lista_prezzi_medi.append((distributore.nome, media)) # distributore.nome mi da il nome del distributore, che è attributo dell'oggetto
        return lista_prezzi_medi


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # Ricorsione esplorativa
        if giorno > 7:
            if self.__costo_ottimo == -1: # Prima soluzione, va salvata
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = copy.deepcopy(sequenza_parziale) # Se non copio la lista, il backtracking mi svuota completamente anche la lista delle soluzioni

            elif costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = copy.deepcopy(sequenza_parziale)
        else:
            for distributore in self._distributori:
                costo_temporaneo = costo_corrente
                 # Creata per non trascinare calcoli residui da ogni iterazione
                if ultimo_distributore is not None and distributore.id != ultimo_distributore: # Verifico se aggiungere la "tassa fissa"
                    costo_temporaneo = costo_corrente + 5
                distributore_temp = distributore.id # L'ultimo diventa quello corrente
                costo_temporaneo += (prezzi_settimana[distributore.id][giorno-1])*100 # Ricordando che prezzi_settimana è un dizionario, sommo al prezzo totale il prezzo giornaliero
                sequenza_parziale.append(distributore.id) # Aggiungo il distributore alla sequenza parziale, per poter salvare le scelte fatte finora
                self.__ricorsione(sequenza_parziale, giorno + 1, distributore_temp, costo_temporaneo, prezzi_settimana) # Ricorro chiamando i parametri correnti, va dentro al ciclo for per poter salvare ogni iterazione
                # giorno + 1 importante per avanzare di giorno ad ogni fine ciclo
                sequenza_parziale.pop() # Backtracking: disfo l'ultima scelta per ripristinare lo stato precedente e esplorare un nuovo ramo


    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        diz_prima_settimana = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()  # Recupero tutti i prezzi del singolo distributore dal DTO
            prezzi_prima_settimana = []
            for prezzo in prezzi:
                if prezzo.data.month == mese and prezzo.data.day <= 7:  # Controllo il mese e che il giorno appartenga ai primi 7 del mese con .data.day (attributo della classe Data)
                    prezzi_prima_settimana.append(prezzo.prezzo_litro)
            diz_prima_settimana[distributore.id] = prezzi_prima_settimana

        return diz_prima_settimana
