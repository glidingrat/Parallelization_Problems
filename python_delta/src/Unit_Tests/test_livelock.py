import unittest
from src.Parallelization_Problems.Livelock import Resource, Process

class TestResource(unittest.TestCase):
    """
    Jednotkové testy pro detekci a zpracování situací spojených s Livelockem.
    Tato třída testuje mechanismy získávání a uvolňování zdrojů
    a detekci livelocku mezi procesy.
    """

    def test_acquire_resource(self):
        """
        Test získání zdroje v daném časovém limitu.
        Tento test kontroluje, zda proces může úspěšně získat zámek zdroje
        před vypršením časového limitu.
        """
        resource = Resource("TestResource")
        process_name = "TestProcess"
        self.assertTrue(resource.acquire(process_name, timeout=1))  # Testujeme, zda je zámek získán v rámci časového limitu

    def test_acquire_resource_timeout(self):
        """
        Test získání zámku zdroje, když dojde k vypršení časového limitu.
        Tento test zajišťuje, že pokud proces nemůže získat zámek v rámci
        určeného časového limitu, vrátí False.
        """
        resource = Resource("TestResource")
        process_name = "TestProcess"

        # Simulujeme, že zámek je již získán
        resource.lock.acquire()

        # Testujeme, že acquire vyvolá TimeoutError, když nelze zámek získat do 0,5s
        with self.assertRaises(TimeoutError):
            resource.acquire(process_name, timeout=0.5)

    def test_process_livelock_detection(self):
        """
        Test detekce livelocku mezi dvěma procesy.
        Tento test simuluje dva procesy, které se pokoušejí zamknout zdroje v opačném pořadí,
        což způsobí situaci livelocku. Test kontroluje, zda byl livelock detekován.
        """
        resource1 = Resource("Resource 1")
        resource2 = Resource("Resource 2")

        # Procesy zamknou zdroje v opačném pořadí, což způsobí livelock
        process1 = Process("Process 1", resource1, resource2)
        process2 = Process("Process 2", resource2, resource1)

        process1.start()
        process2.start()

        process1.join()
        process2.join()

        # Ověřujeme, zda byl livelock detekován
        self.assertTrue(process1.livelock_detected or process2.livelock_detected)

if __name__ == '__main__':
    unittest.main()
