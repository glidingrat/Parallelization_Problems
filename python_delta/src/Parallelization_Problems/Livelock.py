import threading
import time
import json

output_lock = threading.Lock()  # Zámek pro synchronizaci výstupu


# Třída reprezentující zdroje, které budou zamykány
class Resource:
    def __init__(self, name):
        """
        Inicializuje objekt Resource se zadaným názvem.

        :param name: Název zdroje
        :raises ValueError: Pokud název není řetězec nebo je prázdný
        """
        if not isinstance(name, str):
            raise ValueError("Název zdroje musí být řetězec.")
        if len(name) == 0:
            raise ValueError("Název zdroje nesmí být prázdný.")
        self.name = name
        self.lock = threading.Lock()  # Zámek pro synchronizaci přístupu

    def acquire(self, process_name, timeout=5):
        """
        Pokusí se zamknout zdroj v rámci zadaného časového limitu.
        Pokud zámek nelze získat včas, vyvolá výjimku.

        :param process_name: Název procesu, který se pokouší zdroj zamknout
        :param timeout: Čas (v sekundách) pro pokus o zamknutí (výchozí 5 sekund)
        :raises ValueError: Pokud název procesu není řetězec nebo je prázdný
        :raises TimeoutError: Pokud zámek nelze získat během časového limitu
        """
        if not isinstance(process_name, str):
            raise ValueError("Název procesu musí být řetězec.")
        if len(process_name) == 0:
            raise ValueError("Název procesu nesmí být prázdný.")

        start_time = time.time()
        while time.time() - start_time < timeout:
            acquired = self.lock.acquire(blocking=False)
            if acquired:
                return True

            time.sleep(1)  # Pauza před dalším pokusem
        raise TimeoutError(f"Timeout: Proces '{process_name}' nemohl zamknout '{self.name}'")  # Výjimka při timeoutu


# Třída reprezentující procesy, které budou pracovat se zdroji
class Process(threading.Thread):
    def __init__(self, name, resource1, resource2):
        """
        Inicializuje objekt Process se zadanými zdroji.

        :param name: Název procesu
        :param resource1: První zdroj k zamknutí
        :param resource2: Druhý zdroj k zamknutí
        :raises ValueError: Pokud název procesu není řetězec nebo zdroje nejsou instancemi třídy Resource
        """
        if not isinstance(name, str):
            raise ValueError("Název procesu musí být řetězec.")
        if len(name) == 0:
            raise ValueError("Název procesu nesmí být prázdný.")
        if not isinstance(resource1, Resource) or not isinstance(resource2, Resource):
            raise ValueError("Zdroje musí být instance třídy Resource.")

        threading.Thread.__init__(self)
        self.name = name
        self.resource1 = resource1
        self.resource2 = resource2
        self.livelock_detected = False  # Stav detekce livelocku

    def run(self):
        """
        Spustí proces, který se pokusí zamknout oba zdroje.
        Pokud je detekován livelock (opakované neúspěšné pokusy), bude označen.
        """
        attempts = 0
        while attempts < 3:  # Pár pokusů
            with output_lock:
                print(f'{self.name}: pokus o zamknutí {self.resource1.name}')
            try:
                if self.resource1.acquire(self.name):  # Pokus o zamknutí prvního zdroje
                    with output_lock:
                        print(f'{self.name}: zamknul {self.resource1.name}')

                    time.sleep(1)  # Simulace čekání na druhý zdroj

                    with output_lock:
                        print(f'{self.name}: pokus o zamknutí {self.resource2.name}')
                    try:
                        if self.resource2.acquire(self.name):  # Pokus o zamknutí druhého zdroje
                            with output_lock:
                                print(f'{self.name}: zamknul {self.resource2.name}')
                            break  # Dokončení práce
                        else:
                            raise Exception(f"{self.name}: nepodařilo se zamknout {self.resource2.name}")
                    except TimeoutError as e:
                        with output_lock:
                            print(e)
                        self.resource1.lock.release()  # Uvolnění prvního zdroje
            except TimeoutError as e:
                with output_lock:
                    print(e)
            except Exception as e:
                with output_lock:
                    print(f"{self.name}: Chyba: {e}")

            attempts += 1
            time.sleep(0.5)  # Pauza před dalším pokusem

        # Detekce livelocku pouze při opakovaných neúspěšných pokusech
        if attempts == 3:
            with output_lock:
                print(f'{self.name}: Livelock detekován!')
            self.livelock_detected = True  # Označení detekce livelocku


def load_config(config_file):
    """
    Načte konfiguraci ze souboru.

    :param config_file: Cesta ke konfiguračnímu souboru
    :return: Načtená konfigurace ve formátu slovníku
    :raises FileNotFoundError: Pokud soubor neexistuje
    :raises ValueError: Pokud soubor obsahuje neplatný JSON
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Konfigurační soubor '{config_file}' nebyl nalezen.")
    except json.JSONDecodeError:
        raise ValueError(f"Chyba při dekódování JSON v konfiguračním souboru '{config_file}'.")


if __name__ == "__main__":
    try:
        config = load_config('../config/config.json')

        # Vytvoření resources na základě konfigurace
        resources = {}
        for key, value in config['deadlock_livelock']['resources'].items():
            try:
                resources[key] = Resource(value['name'])
            except ValueError as e:
                with output_lock:
                    print(f"Chyba při vytváření zdroje '{key}': {e}")

        # Vytvoření procesů na základě konfigurace
        processes = []
        for p in config['deadlock_livelock']['processes']:
            try:
                resource1 = resources[p['resource1']]
                resource2 = resources[p['resource2']]
                process = Process(p['name'], resource1, resource2)
                processes.append(process)
            except KeyError as e:
                with output_lock:
                    print(f"Chyba: Zdroj '{e}' nebyl nalezen pro proces '{p['name']}'")
            except ValueError as e:
                with output_lock:
                    print(f"Chyba: {e}")

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        if any(process.livelock_detected for process in processes):
            with output_lock:
                print(
                    "\nLIVELOCK DETEKOVÁN: Oba procesy se pokoušely získat zdroje, opakovaně je uvolňovaly a zkoušely znovu bez pokroku.")
        else:
            with output_lock:
                print("\nLivelock nebyl detekován. Oba procesy úspěšně dokončily svou práci.")

    except Exception as e:
        with output_lock:
            print(f"CHYBA: {e}")
