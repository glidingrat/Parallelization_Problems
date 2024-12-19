import threading
import time
import json

output_lock = threading.Lock()  # Synchronizační zámek pro výstup


def load_config(config_file):
    """
    Načte konfiguraci ze zadaného JSON souboru.

    Argumenty:
        config_file (str): Cesta ke konfiguračnímu souboru.

    Návratová hodnota:
        dict: Načtená konfigurace.

    Výjimky:
        FileNotFoundError: Pokud konfigurační soubor není nalezen.
        ValueError: Pokud konfigurační soubor nelze dekódovat.
        Exception: Pokud při načítání konfigurace nastane chyba.
    """
    try:
        if not isinstance(config_file, str):
            raise ValueError("Cesta ke konfiguračnímu souboru musí být řetězec.")

        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Konfigurační soubor '{config_file}' nebyl nalezen.")
    except json.JSONDecodeError:
        raise ValueError(f"Nelze dekódovat JSON z konfiguračního souboru '{config_file}'.")
    except Exception as e:
        raise Exception(f"Při načítání konfigurace nastala chyba: {e}")


class Resource:
    def __init__(self, name):
        """
        Inicializuje zdroj se specifikovaným názvem.

        Argumenty:
            name (str): Název zdroje.

        Výjimky:
            ValueError: Pokud název zdroje není neprázdný řetězec.
        """
        if not isinstance(name, str):
            raise ValueError("Název zdroje musí být řetězec.")
        if not name.strip():
            raise ValueError("Název zdroje nesmí být prázdný nebo pouze mezery.")

        self.name = name
        self.lock = threading.Lock()

    def acquire(self, process_name):
        """
        Uzamkne zdroj, pokud je zámek dostupný.

        Argumenty:
            process_name (str): Název procesu, který se pokouší zdroj uzamknout.

        Výjimky:
            ValueError: Pokud název procesu není neprázdný řetězec.
            Exception: Pokud při uzamykání zdroje nastane chyba.
        """
        try:
            if not isinstance(process_name, str) or not process_name.strip():
                raise ValueError(f"Název procesu musí být neprázdný řetězec. Zadané: {process_name}")

            self.lock.acquire(timeout=5)
        except Exception as e:
            raise Exception(f"Chyba při uzamykání zdroje '{self.name}' procesem '{process_name}': {e}")

    def release(self):
        """
        Uvolní zámek zdroje.

        Výjimky:
            RuntimeError: Pokud zámek není aktuálně uzamčen.
        """
        try:
            self.lock.release()
        except RuntimeError:
            raise RuntimeError(f"Pokusu o uvolnění zámku zdroje '{self.name}' se nezdařilo, zámek není uzamčen.")


class Process(threading.Thread):
    def __init__(self, name, resource, priority=1):
        """
        Inicializuje proces se zadaným názvem, přidruženým zdrojem a prioritou.

        Argumenty:
            name (str): Název procesu.
            resource (Resource): Zdroj, který se proces pokusí uzamknout.
            priority (int): Priorita procesu (nižší hodnota znamená vyšší prioritu).

        Výjimky:
            ValueError: Pokud je název procesu, zdroj nebo priorita neplatná.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Název procesu musí být neprázdný řetězec.")
        if not isinstance(resource, Resource):
            raise ValueError("Zdroj musí být instancí třídy Resource.")
        if not isinstance(priority, int) or priority < 1:
            raise ValueError("Priorita musí být kladné celé číslo.")

        threading.Thread.__init__(self)

        self.name = name
        self.resource = resource
        self.priority = priority
        self.starved = False
        self.attempts = 0

    def run(self):
        """
        Spustí proces, který se pokouší uzamknout zdroj až čtyřikrát.

        Pokud proces nemůže zdroj uzamknout kvůli vyhladovění, přestane se pokoušet.
        """
        try:
            while self.attempts < 4:
                if self.starved:
                    break

                with output_lock:
                    print(f'{self.name}: pokouší se uzamknout {self.resource.name}')

                try:
                    if self.priority == 1:
                        self.resource.acquire(self.name)

                        with output_lock:
                            print(f'{self.name}: uzamkl {self.resource.name}')
                        time.sleep(3)
                        self.resource.release()
                        with output_lock:
                            print(f'{self.name}: uvolnil {self.resource.name}')
                    else:
                        time.sleep(2)

                    self.attempts += 1

                except Exception as e:
                    with output_lock:
                        print(f'{self.name}: {e}')
                    break

            if self.attempts >= 4 and self.priority > 1:
                with output_lock:
                    print(f'{self.name}: byl vyhladován (nemožnost uzamknout zdroj).')
                self.starved = True
            else:
                self.starved = False
        except Exception as e:
            with output_lock:
                print(f"CHYBA v procesu {self.name}: {e}")
            self.starved = True


if __name__ == "__main__":
    try:
        config = load_config('../config/config.json')

        if "starvation" not in config:
            raise KeyError("V konfiguraci chybí sekce 'starvation'.")

        # Vytvoření resources na základě konfigurace
        resources = {}
        for resource_name, resource_config in config["starvation"]["resources"].items():
            if "name" not in resource_config:
                raise KeyError(f"Zdroj '{resource_name}' postrádá v konfiguraci 'name'.")
            resources[resource_name] = Resource(resource_config["name"])

        # Vytvoření procesů na základě konfigurace
        processes = []
        for process_config in config["starvation"]["processes"]:
            if "name" not in process_config or "resource" not in process_config or "priority" not in process_config:
                raise KeyError("Konfigurace procesu musí obsahovat 'name', 'resource' a 'priority'.")
            process_name = process_config["name"]
            resource_name = process_config["resource"]
            priority = process_config["priority"]

            if resource_name not in resources:
                raise ValueError(f"Zdroj '{resource_name}' nebyl nalezen pro proces '{process_name}'.")

            process = Process(process_name, resources[resource_name], priority)
            processes.append(process)

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        starving_processes = [process.name for process in processes if process.starved]

        if starving_processes:
            with output_lock:
                print("\nSTARVATION DETEKOVÁN: Následující procesy nemohly uzamknout zdroj kvůli opakovanému uzamčení jinými procesy:")
                for process in starving_processes:
                    print(f"- {process}")
        else:
            with output_lock:
                print("\nVyhladovění nebylo detekováno. Všechny procesy úspěšně dokončily činnost.")

    except FileNotFoundError as e:
        with output_lock:
            print(f"CHYBA: {e}")
    except KeyError as e:
        with output_lock:
            print(f"CHYBA: {e}")
    except ValueError as e:
        with output_lock:
            print(f"CHYBA: {e}")
    except Exception as e:
        with output_lock:
            print(f"CHYBA: {e}")
