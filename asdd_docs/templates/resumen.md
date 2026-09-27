# RESUMEN de verificación — [Nombre de la feature]
_Plan: asdd_docs/plans/YYYY-MM-DD-<feature>.md_
_SPEC: asdd_docs/specs/YYYY-MM-DD-<feature>.md_
_Modo: paralelo (subagentes) | secuencial (agente único)_
_Inicio → fin: YYYY-MM-DD HH:MM → YYYY-MM-DD HH:MM_

## Oleadas
| Oleada | Tipo | Tareas | Resultado |
|--------|------|--------|-----------|
| 1 | paralela | T01, T02 | OK |
| 2 | secuencial | T03 | OK |

## Tareas y nivel de prueba
| Tarea | Verificación | Prueba | Último resultado |
|-------|--------------|--------|------------------|
| T01 | local | Evidencia capturada (asdd-verify) | ✅ exit 0 |
| T02 | auto | Reejecutada por la CI en cada PR | ✅ exit 0 |
| T03 | manual | Confirmada por el responsable | ✅ |
| T_FINAL | auto | Reejecutada por la CI en cada PR | ✅ exit 0 |

## Revisión de integración
[Tras cada oleada paralela: revisión conjunta de los cambios. Conflictos detectados y cómo se resolvieron.]

## Criterios de aceptación
| CA | Resultado | Evidencia |
|----|-----------|-----------|
| CA1 | ✓ | verifications/<feature>/T_FINAL.md |
| CA2 | ✓ | verifications/<feature>/T_FINAL.md |

## Incidencias y desviaciones
[Resumen de lo que se salió del plan y cómo se resolvió.]

## Pendiente / fuera de alcance
[Lo que pasa a un SPEC futuro.]
