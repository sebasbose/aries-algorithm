# Reporte del laboratorio #3
**C11142 - Sebastián Bolaños Serrano**

## Que es ARIES?
El algoritmo ARIES es un metodo de recuperación de bases de datos desarrollado por IBM. Es bastante popular en sistemas transaccionales como el motor de PostgresSQL o SQL Server.

Su función principal es garantizar que la base de datos pueda recueprarse a un estado consistente tras un fallo (como una caida del sistema o una falla de hardware).

## Como funciona?
El algoritmo ARIES se basa en tres principios clave: Write-Ahead Logging, Repeating history during redo, y Undo of loser transactions. 

1. Write-Ahead Logging (WAL): previo a cualquier modificación, se registra la operación a realizar en un log. 
2. Reapeating history during redo: el algoritmo repite todas las operaciones registradas en el log.
3. Undo of loser transactions: finalmente, el algoritmo detecta las operaciones que no fueron confirmadas y las revierte (deshace).

Entonces, el algoritmo funciona por medio de tres estapas de recuperación: Analysis, Redo y Undo.

1. Analysis: se determinan las transacciones que estaban activas y las página que fueron modificadas.
2. Redo: replica o "rehace" los cambios de un log para dejar todo como estaba antes de la falla.
3. Undo: revierte las transacciones incompletas, tambien conocidas como (perdedoras o losers).

## Como ejecutar el script?
Para ejecutar el script `aries.py` se correr el siguiente comando.

```
python aries.py <log_file.txt>
```

**Importante:** actualmente eixsten 4 log files en la carpte `./logs/`, si se desea utilizar otro caso de prueba, debes crear un archivo `.txt` y pegar el caso de prueba ahi.

## Creditos, Referencias y Bibliografia
### URLs y sitios web consultados:
- https://en.wikipedia.org/wiki/Algorithms_for_Recovery_and_Isolation_Exploiting_Semantics
- https://www.geeksforgeeks.org/dbms/algorithm-for-recovery-and-isolation-exploiting-semantics-aries/

### En formato APA:
- [1] Wikimedia Foundation. (2025, August 2). Algorithms for recovery and isolation exploiting semantics. Wikipedia. https://en.wikipedia.org/wiki/Algorithms_for_Recovery_and_Isolation_Exploiting_Semantics 

- [2] GeeksforGeeks. (2025, August 13). Algorithm for recovery and isolation exploiting semantics (Aries). https://www.geeksforgeeks.org/dbms/algorithm-for-recovery-and-isolation-exploiting-semantics-aries/ 

### Sobre el uso de IA en este laboratorio:
Aprovecho este espacio para anotar y declarar que para la realización de este laboratorio se utilizaron, en partes y no en su totalidad, herramientas de inteligencia artificial para la implementación del simulador del algoritmo ARIES. Especificamente para la generación de Logs para pruebas y partes de la logica del archivo `aries.py`, como prints y solución de errores.

Para la confección de este reporte y la investigación sobre el funcionamiento del algoritmo, no se utilizó ninguna herramienta de inteligencia artificial. En cuanto al desarrollo, la mayoria de la lógica fue desarrollada de manera independiente.

Aclaro que comprendo la logica, funcionamiento y estructura del algoritmo, el uso de herramientas de IA para el desarrollo de algunas partes del script de simulación fue estrictamente para aumentar la mi eficiencia y productividad.