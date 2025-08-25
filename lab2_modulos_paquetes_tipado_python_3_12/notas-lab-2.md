🔹 Importaciones absolutas

Se usan cuando importamos desde fuera del paquete.

Ventaja: Son más claras y explícitas, evitan confusiones al mover módulos.

Ejemplo: from A_modulos.operaciones_aritmeticas import suma

Importaciones relativas

Se usan dentro del mismo paquete, cuando un módulo necesita otro módulo hermano.

Ventaja: Mantiene independencia del nombre del paquete (útil si cambias el nombre o anidas).

Ejemplo: from . import operaciones_aritmeticas as op

🔹 __init__.py
Convierte la carpeta en un paquete Python.

En este caso, reexportamos 'suma', 'obtener_texto_suma', 'ejecutar_operaciones' porque son las funciones más usadas.

Esto permite: from A_modulos import suma, obtener_texto_suma, from A_modulos import ejecutar_operaciones
