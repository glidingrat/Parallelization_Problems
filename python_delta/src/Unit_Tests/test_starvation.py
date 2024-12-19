import unittest
import time
from src.Parallelization_Problems.Starvation import Resource, Process

class TestStarvation(unittest.TestCase):
    """
    Jednotkové testy pro detekci a zpracování situací spojených s hloubkou (Starvation).
    Tato třída testuje chování procesů s různými prioritami
    pro zajištění detekce hloubky a správného zacházení se zdroji.
    """

    def setUp(self):
        """
        Metoda pro nastavení testovacího prostředí před každým testem.
        Vytváří nový zdroj pro každý test.
        """
        self.resource = Resource("Testovací zdroj")

    def test_high_priority_process_locks_resource(self):
        """
        Test, že proces s vysokou prioritou dokáže získat zámek zdroje.
        Tento test kontroluje, zda proces s vysokou prioritou dokáže získat zámek bez toho, aby došlo k hloubce.
        """
        process = Process("Proces s vysokou prioritou", self.resource, priority=1)
        process.start()
        process.join()

        # Ověření, že proces s vysokou prioritou získal zámek
        self.assertFalse(process.starved)

    def test_low_priority_process_is_starved(self):
        """
        Test, že proces s nízkou prioritou je hladoví, když proces s vyšší prioritou drží zdroj.
        Tento test zajišťuje, že procesy s nižší prioritou mohou být hladoví, pokud čekají na zdroj.
        """
        process1 = Process("Proces s vysokou prioritou", self.resource, priority=1)
        process2 = Process("Proces s nízkou prioritou", self.resource, priority=2)

        process1.start()
        process2.start()

        process1.join()
        process2.join()

        # Ověření, že proces s nízkou prioritou je starved
        self.assertTrue(process2.starved)

    def test_multiple_processes_starvation_detection(self):
        """
        Test, zda je správně detekována hloubka ve scénáři s více procesy.
        Tento test kontroluje, zda procesy s nižšími prioritami jsou hladoví, když čekají na zdroj.
        """
        process1 = Process("Proces 1", self.resource, priority=1)
        process2 = Process("Proces 2", self.resource, priority=2)
        process3 = Process("Proces 3", self.resource, priority=3)

        process1.start()
        process2.start()
        process3.start()

        process1.join()
        process2.join()
        process3.join()

        # Ověření, že procesy 2 a 3 jsou starved
        self.assertTrue(process2.starved)
        self.assertTrue(process3.starved)

    def test_resource_lock_and_release(self):
        """
        Test, že zámek zdroje je správně získán a uvolněn.
        Tento test zajišťuje, že proces může získat zámek, provést úkol a uvolnit zámek.
        """
        process1 = Process("Proces 1", self.resource, priority=1)
        process1.start()

        # Simulace krátkého zpoždění
        time.sleep(1)

        # Proces by měl mít zámek a neměl by být starved
        self.assertFalse(process1.starved)

        # Počkáme, až proces dokončí svůj úkol
        process1.join()


if __name__ == '__main__':
    unittest.main()
