# Taller de Spec-Driven Development (SDD)

## Objetivo

Analizar y mejorar una especificación de requisitos elaborada con asistencia de inteligencia artificial.

El objetivo no es aceptar automáticamente lo que propone la IA, sino evaluar la calidad de los requisitos, identificar ambigüedades y justificar las decisiones de mejora.

## Caso de estudio

Una aplicación simple que gestiona tareas personales.

La especificación inicial se encuentra en `requirements/spec-inicial.md`.

## Actividades

1. Leer la especificación completa.
2. Identificar al menos tres ambigüedades, supuestos o decisiones pendientes.
3. Proponer mejoras a los criterios de aceptación.
4. Utilizar IA para explorar alternativas y evaluar críticamente sus propuestas.
5. Documentar las decisiones finales y justificarlas.

## Entregables

- Una especificación revisada.
- Al menos tres decisiones de mejora justificadas.
- Una reflexión breve sobre las limitaciones de utilizar IA para definir requisitos.

## Principio de trabajo

Cada cambio debe responder a una necesidad identificada y contar con una justificación.

No es necesario implementar la aplicación en este taller.

## Estructura del repositorio

- `requirements/`: especificación inicial.
- `activities/`: guía de trabajo.
- `deliverables/`: resultados de los estudiantes.

## Aplicación Curso-PSWE-07

La implementación de referencia utiliza Python 3.11+ y Textual 8.2.8 para una
interfaz de pantalla completa, estilo DOS. El taller anterior sigue siendo válido
sin implementar la aplicación.

### Instalación y ejecución

Desde la raíz del repositorio, con un intérprete Python 3.11 o posterior:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m curso_pswe_07
```

En PowerShell, usar `py -3.11 -m venv .venv` y
`.venv\Scripts\Activate.ps1` para crear y activar el entorno. Si `python3` es una
versión anterior a 3.11, seleccionar primero un intérprete compatible.

Se requiere una terminal interactiva de al menos **80 columnas por 24 filas**.
No existe una interfaz alternativa por comandos. La aplicación permite una sola
sesión activa; después de instalar las dependencias funciona sin conexión.

### Uso

- **Tab / Shift+Tab**: cambiar de control; flechas: recorrer tareas y menús.
- **Enter / Espacio**: activar botones; Enter sobre una tarea abre su detalle.
- **Home / End / PageUp / PageDown**: recorrer una lista larga. En el detalle,
  las flechas y PageUp/PageDown desplazan el contenido.
- **Add task / Edit**: título obligatorio y descripción opcional. Guardar requiere
  activar **Save**. Enter en la descripción inserta una nueva línea; **F7**
  selecciona todo el texto de ese campo.
- **All / Pending / Done**: filtrar tareas sin modificar los datos.
- **Delete**: requiere confirmación; **Cancel** tiene el foco inicial.
- **Escape**: cancelar un diálogo o volver desde el detalle.
- **Exit / Ctrl+Q**: salir; **Ctrl+C**: interrumpir. Ninguno guarda un borrador.

Las tareas se guardan después de cada cambio confirmado en
`~/.curso-pswe-07/tasks.json` (carpeta personal del usuario). Si falla una carga,
se muestra el error y se abre una **lista temporal**, con un aviso permanente:
sus cambios nunca se escriben al archivo y se pierden al cerrar. La siguiente
sesión vuelve a intentar cargar el archivo original.

Reducir la terminal por debajo del mínimo muestra un aviso y bloquea cambios,
sin descartar el borrador ni la selección.

### Pruebas y alcance de validación

```sh
python -m unittest discover -s tests -v
```

Las pruebas usan archivos y carpetas personales temporales; no modifican las
tareas reales. Incluyen lógica de negocio, almacenamiento atómico, navegación,
diálogos, redimensionado, rendimiento y procesos con PTY en POSIX. Las pruebas
PTY se omiten explícitamente en Windows y no sustituyen su validación manual.

Consultar [la guía de validación](specs/001-manage-daily-tasks/quickstart.md) para
la evidencia, los requisitos y las validaciones pendientes. No se incluyen
cuentas, categorías, fechas, prioridades, búsqueda ni sincronización.