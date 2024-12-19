import unittest
import threading
import time
from src.Parallelization_Problems.Deadlock import Resource, Process

class TestDeadlock(unittest.TestCase):
    """
    Jednotkové testy pro problémy spojené s Deadlockem v paralelizovaných úlohách.
    Tato třída testuje mechanismy získávání a uvolňování zdrojů
    a detekci deadlocku mezi procesy.
    """

    def test_acquire_resource_success(self):
        """
        Testuje, že metoda acquire správně zamkne zdroj.
        Tento test zajišťuje, že zdroj je uzamčen, když jej proces získá.
        """
        resource = Resource("TestResource")
        resource.acquire("TestProcess")
        self.assertTrue(resource.lock.locked())

    def test_acquire_resource_timeout(self):
        """
        Testuje metodu acquire s timeoutem.
        Tento test simuluje situaci, kdy je zdroj zamknutý dlouhou dobu, a kontroluje,
        zda mechanismus timeoutu správně vyvolá TimeoutError.
        """
        resource = Resource("TestResource")

        def lock_resource():
            resource.lock.acquire()
            time.sleep(2)  # Zpoždění pro simulaci dlouhého zamknutí

        lock_thread = threading.Thread(target=lock_resource)
        lock_thread.start()

        start_time = time.time()
        with self.assertRaises(TimeoutError):
            resource.acquire("TestProcess", timeout=0.5)
        lock_thread.join()

        self.assertGreater(time.time() - start_time, 0.5)

    def test_process_success(self):
        """
        Testuje, že proces správně zamkne oba zdroje.
        Tento test zajišťuje, že když proces získá více zdrojů, úspěšně je zamkne bez deadlocku.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")
        process = Process("TestProcess", resource1, resource2)

        process.start()
        process.join()

        self.assertFalse(process.deadlock_detected)  # Deadlock by neměl být detekován
        self.assertTrue(resource1.lock.locked())  # Zdroje by měly být zamknuté
        self.assertTrue(resource2.lock.locked())  # Zdroje by měly být zamknuté

    def test_process_deadlock(self):
        """
        Testuje, že deadlock nastane, když procesy zamknou zdroje v opačném pořadí.
        Tento test simuluje scénář deadlocku, kdy dva procesy zamknou zdroje
        v opačném pořadí, což způsobí deadlock.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")

        process1 = Process("Process 1", resource1, resource2)
        process2 = Process("Process 2", resource2, resource1)

        process1.start()
        process2.start()
        process1.join()
        process2.join()

        self.assertTrue(process1.deadlock_detected)
        self.assertTrue(process2.deadlock_detected)

    def test_invalid_resource_name(self):
        """
        Test pro neplatný název zdroje.
        Tento test kontroluje, že bude vyvolána výjimka, pokud je zdroj vytvořen s neplatným názvem (neřetězcový).
        """
        with self.assertRaises(ValueError):
            Resource(123)  # Název musí být řetězec

    def test_process_creation(self):
        """
        Test pro vytvoření procesu.
        Tento test zajišťuje, že proces je správně vytvořen s daným názvem a zdroji.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")
        process = Process("Process 1", resource1, resource2)
        self.assertEqual(process.name, "Process 1")
        self.assertEqual(process.resource1, resource1)
        self.assertEqual(process.resource2, resource2)

    def test_invalid_process_name(self):
        """
        Test pro neplatný název procesu.
        Tento test kontroluje, že bude vyvolána výjimka, pokud je proces vytvořen s neplatným názvem (neřetězcový).
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")
        with self.assertRaises(ValueError):
            Process(123, resource1, resource2)  # Název musí být řetězec

    def test_deadlock_detection(self):
        """
        Test detekce deadlocku mezi dvěma procesy.
        Tento test zajišťuje, že deadlock je detekován, když dva procesy čekají na uvolnění zdrojů,
        které si vzájemně drží.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")
        process1 = Process("Process 1", resource1, resource2)
        process2 = Process("Process 2", resource2, resource1)

        process1.start()
        process2.start()

        process1.join()
        process2.join()

        self.assertTrue(process1.deadlock_detected or process2.deadlock_detected, "Deadlock nebyl detekován.")

    def test_acquire_with_timeout(self):
        """
        Test získání zdrojů s timeoutem.
        Tento test kontroluje, že deadlock bude detekován, když dva procesy budou chtít zamknout zdroje
        v pořadí, které vede k deadlockové situaci.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")

        process1 = Process("Process 1", resource1, resource2)
        process2 = Process("Process 2", resource2, resource1)

        process1.start()
        process2.start()

        process1.join()
        process2.join()

        self.assertTrue(process1.deadlock_detected or process2.deadlock_detected, "Deadlock nebyl detekován.")

    def test_multiple_deadlocks(self):
        """
        Test pro více deadlocků mezi dvěma procesy.
        Tento test zajišťuje, že detekce deadlocku funguje pro složitější scénáře zahrnující více deadlocků.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")

        process1 = Process("Process 1", resource1, resource2)
        process2 = Process("Process 2", resource2, resource1)

        thread1 = threading.Thread(target=process1.run)
        thread2 = threading.Thread(target=process2.run)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        self.assertTrue(process1.deadlock_detected, "Deadlock nebyl detekován v procesu 1.")
        self.assertTrue(process2.deadlock_detected, "Deadlock nebyl detekován v procesu 2.")

if __name__ == "__main__":
    unittest.main()
