# Protocolo de debugging

Cuando una verificación falla o algo "que debería funcionar" no funciona.

1. **Para.** No toques más archivos. No "pruebes a ver" cambios encadenados.
2. **Reproduce.** Ejecuta de nuevo la verificación exacta con `asdd-verify.sh` (queda registrada).
3. **Acota.** ¿Falla siempre o a veces? ¿Con qué input? ¿Desde qué cambio? (`git diff`,
   `git stash` y reintento si hace falta).
4. **Lee el error completo**: stack trace, logs de n8n, logs de Supabase, respuesta HTTP entera.
   No te quedes con la primera línea.
5. **Formula una hipótesis de causa raíz** y una forma de comprobarla sin modificar código
   (un `SELECT`, un `curl`, un `console.log` temporal, leer la config).
6. **Compruébala.** Si no se confirma, vuelve al paso 5. Máximo 3 hipótesis antes de escalar.
7. **Documenta** en el `.md` de la tarea la causa raíz (o hipótesis descartadas). Las evidencias
   fallidas ya las dejó `asdd-verify.sh`.
8. **Reporta** al humano: qué falló, por qué, opciones de arreglo y su impacto en el plan.
9. **Solo con aprobación**: si el arreglo toca archivos no declarados, primero se actualiza el
   plan (y se reaprueba).

Errores típicos a revisar primero: variables de entorno ausentes, credenciales de otro entorno,
RLS de Supabase, formato de fechas/zonas horarias, nodos n8n con "Always Output Data" o
"Continue On Fail" que ocultan errores, caché de despliegues.
