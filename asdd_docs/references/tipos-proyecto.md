# Patrones por tipo de proyecto

## Supabase
- Cambios de esquema **siempre** como migración versionada (`supabase/migrations/…sql`) y en
  **oleada secuencial**. Nunca dos migraciones en paralelo.
- Verificación: `SELECT` que demuestra el cambio (columnas, datos, políticas RLS con el rol
  correcto), no "se aplicó sin error".
- Declara en el plan también las tablas afectadas (en la tabla de recursos) aunque el guard
  solo controle archivos.

## n8n
- Versiona los workflows exportados en JSON (`n8n/<Workflow>.json`) para que el cambio sea un
  archivo declarable y revisable.
- Todos los cambios a un mismo workflow: misma oleada secuencial.
- Verificación: ejecución de prueba con los nodos clave en *success* y el output esperado
  pegado en el acta.

## APIs e integraciones
- Una tarea por endpoint o integración cuando sean independientes (buenas candidatas a paralelo).
- Verificación con `curl` (status + body), incluyendo al menos un caso de error.
- Nunca pegues secretos en actas: enmascáralos (`sk_…XXXX`).

## Scripts Python / JS
- Un archivo por responsabilidad; tareas paralelas si no comparten módulos.
- Verificación: ejecución con input de ejemplo y output esperado.

## Frontend (Astro, React…)
- Componentes distintos → paralelo; estilos o layout globales → secuencial.
- Verificación: build sin errores + comprobación visual descrita (qué se ve, dónde) o test.
