# Simulace problému paralelizace

## Přehled

Tento projekt simuluje Deadlock, Livelock a Starvation pomocí Pythonu a tkinter. Ukazuje, jak tyto problémy vznikají při rozdělování zdrojů mezi procesy a jak mohou být procesy různě prioritizovány.
## Funkce

- **Deadlock**: Simuluje procesy čekající na zdroje druhých procesů, což způsobí věčný stav čekání.  
  **Příklad:** Dva řidiči se snaží projet úzkou silnicí z opačných směrů, ale každý čeká, až ten druhý ustoupí, a nikam se neposunou.

- **Livelock**: Zobrazuje procesy, které neustále mění své stavy bez pokroku kvůli konfliktu.  
  **Příklad**: Dva lidé se snaží projít dveřmi zároveň, ale každý se neustále vyhýbá tomu druhému, takže ani jeden neprojde.

- **Starvation**: Ukazuje, jak procesy s nižší prioritou mohou čekat na zdroje neomezeně dlouho, pokud jsou neustále přerušovány procesy s vyšší prioritou.  
  **Příklad**: V čekárně u lékaře může pacient s méně závažnými příznaky čekat na ošetření dlouho, protože stále přicházejí pacienti s urgentními problémy.

## Jak to funguje

- **GUI**: Jednoduché rozhraní tkinter umožňuje uživatelům vybrat typ simulace. Příslušný Python skript je spuštěn a výstup je zobrazen v reálném čase.
- **Simulace**: Každý typ problému (Deadlock, Livelock, Starvation) je simulován vytvořením příslušného scénáře.

## Tok kódu

1. **Uživatelské rozhraní**: Tlačítka pro výběr simulací (Deadlock, Livelock, Starvation).
2. **Spuštění**: Python skript pro vybranou simulaci běží v samostatném vlákně.
3. **Výstup**: Výstup simulace je zobrazen dynamicky v textovém poli tkinter.

## Spuštění programu

### Možnost 1: Použití IDE (např. PyCharm, Visual Studio Code)

1. Klonujte nebo stáhněte repozitář.
2. Otevřete projektovou složku ve vašem IDE (PyCharm, Visual Studio Code, atd.).
3. Ujistěte se, že jsou nainstalovány všechny potřebné závislosti (např. `tkinter`).
4. Otevřete soubor `GUI.py` ve vašem IDE.
5. Spusťte program kliknutím na tlačítko **Run** nebo pomocí příslušné klávesové zkratky v IDE (např. `Shift + F10` v PyCharm).

### Možnost 2: Použití spustitelného souboru

1. Přejděte do složky `dist` v adresáři projektu.
2. Najděte spustitelný soubor **.exe** (`GUI.exe`).
3. Dvojklikem na soubor spusťte program přímo.

## Testování

- **Deadlock**: Procesy vstoupí do deadlocku, když se pokusí uzamknout zdroje v opačném pořadí.
- **Livelock**: Procesy neustále mění stavy, ale nedochází k žádnému pokroku.
- **Starvation**: Procesy s nižší prioritou jsou hladověny vyššími prioritami.

## Známé problémy

- **Uvolnění zdrojů**: V některých případech nemusí být zdroje uvolněny po simulaci.
- **Vlákna**: Pozadí vlákna nemohou být správně ukončena při ukončení programu.

## Navrhované vylepšení

- **GUI**: Přidání vizuálních prvků, jako jsou grafy nebo diagramy.
- **Zpracování chyb**: Zlepšení zpracování neočekávaných ukončení simulace.
- **Optimalizace**: Vylepšení výkonu simulací s více procesy.

## Odkazy

- **Video tutoriál o paralelizaci**: [YouTube](https://www.youtube.com/watch?v=NUazC4EUG50)
- **Dokumentace tkinter**: [Oficiální Python dokumentace](https://docs.python.org/3/library/tkinter.html)
- **ChatGPT**

---
Krejčiřík Lukáš, C4a :
[GitHub](https://github.com/glidingrat)
---
