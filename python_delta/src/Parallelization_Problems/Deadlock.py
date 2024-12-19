import threading
import time
import json

output_lock = threading.Lock()  # Zámek pro synchronizaci výstupu


class Resource:
    def __init__(self, name):
        """
        Inicializuje objekt Resource se zadaným názvem.

        :param name: Název prostředku
        :raises ValueError: Pokud název není typu string
        """
        if not isinstance(name, str):
            raise ValueError("Název prostředku musí být řetězec.")
        self.name = name
        self.lock = threading.Lock()

    def acquire(self, process_name, timeout=5):
        """
        Pokusí se zamknout prostředek během zadaného timeoutu.
        Pokud se zámek nepodaří získat během timeoutu, vyvolá výjimku.

        :param process_name: Název procesu, který se pokouší zamknout prostředek
        :param timeout: Čas (v sekundách) na pokus o zamčení (výchozí je 5 sekund)
        :raises ValueError: Pokud název procesu není typu string
        :raises TimeoutError: Pokud se zámek nepodaří získat během timeoutu
        """
        if not isinstance(process_name, str):
            raise ValueError("Název procesu musí být řetězec.")

        start_time = time.time()
        while time.time() - start_time < timeout:
            acquired = self.lock.acquire(blocking=False)
            if acquired:
                with output_lock:
                    print(f'{process_name}: {self.name} byl zamčen.')
                return

            time.sleep(1)  # Pauza před dalším pokusem
        raise TimeoutError(f"{self.name}")


class Process(threading.Thread):
    def __init__(self, name, resource1, resource2):
        """
        Inicializuje objekt Process představující proces, který se pokouší zamknout dva prostředky.

        :param name: Název procesu
        :param resource1: První prostředek
        :param resource2: Druhý prostředek
        :raises ValueError: Pokud názvy prostředků nejsou instance třídy Resource
        """
        if not isinstance(name, str):
            raise ValueError("Název procesu musí být řetězec.")
        if not isinstance(resource1, Resource) or not isinstance(resource2, Resource):
            raise ValueError("Prostředky musí být instance třídy Resource.")

        threading.Thread.__init__(self)
        self.name = name
        self.resource1 = resource1
        self.resource2 = resource2
        self.deadlock_detected = False

    def run(self):
        """
        Spustí proces, který se pokouší zamknout oba prostředky.
        Pokud dojde k deadlocku nebo jiné chybě, proces je označen jako neúspěšný.
        """
        try:
            with output_lock:
                print(f'{self.name}: pokus o zamknutí {self.resource1.name}')
            self.resource1.acquire(self.name)  # Pokus o zamknutí prvního prostředku
            with output_lock:
                print(f'{self.name}: zamčen {self.resource1.name}')

            time.sleep(1)  # Simulace čekání na druhý prostředek

            with output_lock:
                print(f'{self.name}: pokus o zamknutí {self.resource2.name}')
            self.resource2.acquire(self.name)  # Pokus o zamknutí druhého prostředku
            with output_lock:
                print(f'{self.name}: zamčen {self.resource2.name}')
        except TimeoutError as e:
            with output_lock:
                print(f"\nCHYBA: {self.name} se pokusil zamknout {e}, ale nepodařilo se.")
                if self.resource1.lock.locked():
                    print(f"  Důvod: {self.resource2.name} byl již zamčen.")
                elif self.resource2.lock.locked():
                    print(f"  Důvod: {self.resource1.name} byl již zamčen.")

            self.deadlock_detected = True
            return
        except Exception as e:
            with output_lock:
                print(f"\nNeočekávaná chyba v procesu {self.name}: {e}")
            self.deadlock_detected = True
            return

        with output_lock:
            print(f'{self.name} dokončil práci.')



def load_config(config_file):
    """
    Načte konfiguraci ze souboru a zpracuje případné chyby.

    :param config_file: Cesta ke konfiguračnímu souboru
    :return: Načtená konfigurace ve formátu slovníku
    :raises FileNotFoundError: Pokud soubor neexistuje
    :raises ValueError: Pokud soubor obsahuje neplatný JSON
    :raises Exception: Pro neočekávané chyby při načítání souboru
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Konfigurační soubor '{config_file}' nebyl nalezen.")
    except json.JSONDecodeError:
        raise ValueError(f"Chyba při dekódování JSON v konfiguračním souboru '{config_file}'.")
    except Exception as e:
        raise Exception(f"Neočekávaná chyba při načítání konfigurace: {e}")



if __name__ == "__main__":
    try:
        config = load_config('../config/config.json')

        # Vytvoření prostředků na základě konfigurace
        if 'deadlock_livelock' not in config:
            raise KeyError("Chybí sekce 'deadlock_livelock' v konfiguraci.")

        if 'resources' not in config['deadlock_livelock'] or 'processes' not in config['deadlock_livelock']:
            raise KeyError("Chybí 'resources' nebo 'processes' v sekci 'deadlock_livelock' v konfiguraci.")

        # Vytvoření resources na základě konfigurace
        resources = {}
        for key, value in config['deadlock_livelock']['resources'].items():
            if 'name' not in value:
                raise KeyError(f"Chybí 'name' pro prostředek '{key}' v konfiguraci.")
            resources[key] = Resource(value['name'])

        # Vytvoření procesů na základě konfigurace
        processes = []
        for p in config['deadlock_livelock']['processes']:
            if 'name' not in p or 'resource1' not in p or 'resource2' not in p:
                raise KeyError(f"Chybí povinná pole pro proces: 'name', 'resource1' nebo 'resource2'.")
            resource1 = resources.get(p['resource1'])
            resource2 = resources.get(p['resource2'])
            if not resource1 or not resource2:
                raise ValueError(f"Prostředky pro proces '{p['name']}' nejsou správně definovány.")
            process = Process(p['name'], resource1, resource2)
            processes.append(process)


        for process in processes:
            process.start()

        for process in processes:
            process.join()

        if any(process.deadlock_detected for process in processes):
            with output_lock:
                print(
                    "\nDEADLOCK DETEKOVÁN: Systém narazil na situaci deadlocku, kdy se procesy navzájem blokovaly.")
        else:
            with output_lock:
                print("\nDeadlock nebyl detekován. Všechny procesy byly úspěšně dokončeny.")

    except Exception as e:
        with output_lock:
            print(f"\nCHYBA: {e}")
