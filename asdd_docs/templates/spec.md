# SPEC: [Nombre del cambio]
_Fecha: YYYY-MM-DD_
_Proyecto: [Kolmai / adopty / adoptaunaia / otro]_

<!-- TIPO DE CAMBIO: elige UNO (el dominante). Si el cambio mezcla tipos (p. ej. refactor + función
     nueva), son DOS SPECs. Sin campo Tipo, la CI lo trata como evolutivo.
       evolutivo   → añadir o ampliar funcionalidad                          (prefijo sugerido: feat-)
       correctivo  → corregir un fallo                                       (prefijo sugerido: fix-)
       adaptativo  → adaptarse a un cambio externo: normativa, SO, API…      (prefijo sugerido: adapt-)
       perfectivo  → mejorar código, rendimiento o seguridad SIN cambiar el
                     comportamiento visible (refactorización)                (prefijo sugerido: refactor-) -->
**Tipo:** evolutivo

## ¿Qué estamos haciendo?
[Descripción en lenguaje natural. Qué problema resuelve. Para quién.]

<!-- ═══ SECCIÓN ESPECÍFICA DEL TIPO: deja SOLO la del tipo elegido y borra las otras tres ═══ -->

## Evolutivo: alcance funcional
- **Qué se añade o amplía:** [funcionalidad nueva, a quién sirve]
- **Cómo lo usará el usuario:** [flujo principal, en pasos]

## Correctivo: el fallo
- **Cómo se reproduce:** [pasos o comando exacto que hoy provoca el fallo]
- **Comportamiento actual:** [qué pasa]
- **Comportamiento esperado:** [qué debería pasar]
- **Causa raíz:** [se completa tras diagnosticar; ver references/debugging.md]
- **Verificación de reproducción:** `[comando que HOY falla y que tras el arreglo debe pasar]`
  <!-- Será la verificación de T_FINAL. Se ejecuta ANTES de tocar código (línea base con fallo). -->

## Adaptativo: el cambio externo
- **Qué ha cambiado fuera:** [normativa, versión de SO/navegador, API deprecada, proveedor…]
- **Referencia:** [enlace a la norma, changelog, aviso de deprecación…]
- **Fecha límite:** [cuándo deja de funcionar o empieza a ser obligatorio]
- **Qué debe seguir funcionando igual:** [lo que no puede romperse con la adaptación]

## Perfectivo: la mejora
- **Qué se mejora:** [código, rendimiento, seguridad, mantenibilidad]
- **Comportamiento que NO puede cambiar:** [lo que el usuario u otros sistemas deben seguir viendo igual]
- **Verificación de comportamiento:** `[comando que comprueba el comportamiento; debe pasar ANTES y DESPUÉS]`
  <!-- Será la verificación de T_FINAL. Se ejecuta ANTES de tocar código (línea base correcta). -->
- **Métrica (si el objetivo es medible):** [p. ej. tiempo de carga 3 s → objetivo ≤ 1 s; cómo se mide]

<!-- ═══ FIN DE SECCIONES ESPECÍFICAS ═══ -->

## ¿Qué NO incluye? (YAGNI)
- [Exclusión 1 — por qué queda fuera]

## Recursos que se tocan
| Recurso | Tipo | Operación |
|---------|------|-----------|
| `tabla_x` | Supabase | INSERT/UPDATE/SELECT |
| `Workflow_Y` | n8n | Modificar nodo Z |
| `src/archivo.py` | Script | Crear/Modificar |

## Criterios de aceptación
(Exactamente cómo sabemos que esto funciona. Verificable, no subjetivo.)
- [ ] CA1: [Condición concreta y verificable]
- [ ] CA2: [Condición concreta y verificable]

## Dependencias y riesgos
- [Qué debe existir o estar configurado]
- [Qué podría fallar y por qué]

## Fuera de alcance de este SPEC
[Todo lo que surja como mejora futura se documenta aquí, no en el código.]

---
<!-- Estado: BORRADOR | APROBADO. Solo el responsable humano marca Aprobado. -->
**Estado:** BORRADOR
**Aprobado:** [ ]
