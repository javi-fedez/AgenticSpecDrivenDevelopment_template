# PLAN: [Nombre de la feature]
_SPEC de referencia: asdd_docs/specs/YYYY-MM-DD-<feature>.md_
_Fecha: YYYY-MM-DD_

## Archivos / recursos afectados
<!-- Primera columna entre backticks: el guard y la CI solo permiten tocar lo que aparece aquí
     o en las líneas "Archivos:" de las tareas. Admite globs (`src/api/*.ts`) y carpetas (`src/api/`). -->
| Archivo/Recurso | Operación | Responsabilidad |
|-----------------|-----------|-----------------|
| `ruta/exacta/archivo.py` | CREAR | [Una sola responsabilidad] |
| `supabase/migrations/2026XXXX_x.sql` | MIGRACIÓN | [Qué cambia] |
| `n8n/Workflow_X.json` | MODIFICAR | [Qué nodo y por qué] |

## Oleadas
<!-- Dentro de una oleada paralela, ninguna tarea comparte archivos ni recursos.
     Migraciones de Supabase y cambios en el mismo workflow de n8n: SIEMPRE oleada secuencial. -->

### Oleada 1 — paralela
- [ ] **T01 — [Nombre corto]**
  - Archivos: `ruta/exacta/a.py`
  - Depende de: —
  - Qué hace: [Descripción concreta]
  - Verificar: [Comando o acción + resultado esperado]

- [ ] **T02 — [Nombre corto]**
  - Archivos: `ruta/exacta/b.py`
  - Depende de: —
  - Qué hace: [Descripción concreta]
  - Verificar: [Comando o acción + resultado esperado]

### Oleada 2 — secuencial
- [ ] **T03 — [Nombre corto]**
  - Archivos: `supabase/migrations/2026XXXX_x.sql`
  - Depende de: T01, T02
  - Qué hace: [Descripción concreta]
  - Verificar: [SELECT que devuelve X]

### Cierre
- [ ] **T_FINAL — Verificación end-to-end**
  - Archivos: —
  - Ejecutar: [Comando o acción que ejerce todo el flujo]
  - Criterios de aceptación del SPEC: CA1 ✓, CA2 ✓, CA3 ✓
  - Done solo si todos los CA pasan

---
<!-- Estado: BORRADOR | APROBADO | EN EJECUCIÓN | COMPLETADO.
     El guard solo deja escribir código con Estado EN EJECUCIÓN + Aprobado [x] (y el SPEC aprobado).
     Solo el responsable humano marca Aprobado. -->
**Estado:** BORRADOR
**Aprobado:** [ ]
