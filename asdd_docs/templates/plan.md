# PLAN: [Nombre de la feature]
_SPEC de referencia: asdd_docs/specs/YYYY-MM-DD-<feature>.md_
_Fecha: YYYY-MM-DD_

<!-- Regla: un SPEC = un PLAN, con el MISMO nombre de archivo. Las verificaciones van en
     asdd_docs/verifications/YYYY-MM-DD-<feature>/ (un .md por tarea + RESUMEN.md). -->

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
     Migraciones de Supabase y cambios en el mismo workflow de n8n: SIEMPRE oleada secuencial.
     Tipo de verificación de cada tarea:
       auto   → la CI vuelve a ejecutar el comando en cada PR (scripts, tests, builds, curl a staging)
       local  → se ejecuta en local con asdd-verify.sh y queda la evidencia (necesita credenciales, sistemas internos)
       manual → no automatizable (revisión visual, llamada de voz…): la confirma el responsable
     T_FINAL debería ser "auto" siempre que sea posible. -->

### Oleada 1 — paralela
- [ ] **T01 — [Nombre corto]**
  - Tipo verificación: local
  - Archivos: `ruta/exacta/a.py`
  - Depende de: —
  - Qué hace: [Descripción concreta]
  - Verificar: `[comando exacto]` → [resultado esperado]

- [ ] **T02 — [Nombre corto]**
  - Tipo verificación: auto
  - Archivos: `ruta/exacta/b.py`
  - Depende de: —
  - Qué hace: [Descripción concreta]
  - Verificar: `[comando exacto]` → [resultado esperado]

### Oleada 2 — secuencial
- [ ] **T03 — [Nombre corto]**
  - Tipo verificación: local
  - Archivos: `supabase/migrations/2026XXXX_x.sql`
  - Depende de: T01, T02
  - Qué hace: [Descripción concreta]
  - Verificar: `[comando que ejecuta el SELECT]` → [resultado esperado]

### Cierre
- [ ] **T_FINAL — Verificación end-to-end**
  - Tipo verificación: auto
  - Archivos: —
  - Verificar: `[comando que ejerce todo el flujo]` → [resultado esperado]
  - Criterios de aceptación del SPEC: CA1 ✓, CA2 ✓, CA3 ✓
  - Done solo si todos los CA pasan

---
<!-- Estado: BORRADOR | APROBADO | EN EJECUCIÓN | COMPLETADO.
     El guard solo deja escribir código con Estado EN EJECUCIÓN + Aprobado [x] (y el SPEC aprobado).
     Solo el responsable humano marca Aprobado. -->
**Estado:** BORRADOR
**Aprobado:** [ ]
