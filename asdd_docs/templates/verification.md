# Verificación TXX — [Nombre de la tarea]
_Plan: asdd_docs/plans/YYYY-MM-DD-<feature>.md_
_Oleada: N (paralela | secuencial) · Tipo de verificación: auto | local | manual_
_Ejecutada por: [implementador subagente | agente único]_

## Qué se hizo
[Descripción concreta de lo implementado. Nada que no estuviera en la tarea.]

## Archivos tocados
- `ruta/archivo` — [creado | modificado]

## Por qué cumple
[Justificación: qué demuestra la verificación y cómo se relaciona con la tarea y con los
criterios de aceptación del SPEC. Si hubo fallos previos, qué se corrigió.]

## Revisión
<!-- La hace un subagente revisor distinto del implementador. En modo secuencial, el propio agente
     en un paso separado, releyendo la tarea y el SPEC. -->
- Cumple la tarea y el SPEC: sí | no — [por qué]
- Calidad: [observaciones]
- Veredicto: PENDIENTE
<!-- Cambiar a "Veredicto: APROBADA" solo cuando la revisión pase. La CI lo exige. -->

## Verificación manual
<!-- SOLO si el tipo es "manual". Describe qué debe comprobar el responsable y dónde.
     Solo el responsable humano marca la casilla. -->
**Verificado por el responsable:** [ ]

## Evidencias
<!-- NO ESCRIBIR AQUÍ A MANO. `./scripts/asdd-verify.sh <feature> TXX -- <comando>` añade debajo un
     bloque por cada ejecución (también las fallidas). La CI valida el último. -->
