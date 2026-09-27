# Bypass de ASDD: el label `asdd-bypass`

`asdd-bypass` es **la única vía válida** para saltarse ASDD. No existen excepciones documentadas,
listas blancas ni variables de entorno. Se usa **solo** cuando no hay alternativa al flujo normal
(por ejemplo, producción caída y sin margen para SPEC y PLAN) y **solo lo pone el responsable
humano del repositorio**. Los agentes tienen prohibido ponerlo, pedirlo a otra herramienta o
sugerirlo: su papel es parar y avisar.

## Qué desbloquea

| Dónde | Efecto |
|-------|--------|
| Local (hook de Claude Code) | El guard permite editar cualquier archivo **en la rama cuyo PR abierto tiene el label**. Lo comprueba con `gh pr view` (caché de 5 minutos en `.asdd/bypass-cache.json`). |
| CI (GitHub Actions) | El check ASDD no valida plan ni actas, **pero exige** la sección `## Motivo del bypass` con contenido real en la descripción del PR. |

En `main`/`master` el bypass nunca aplica en local: siempre se trabaja en una rama con PR.

## 1. Crear el label (una vez por repositorio)

Ya lo hace `scripts/asdd-init.sh`. A mano:

**Con GitHub CLI**
```bash
gh label create asdd-bypass --color B60205 \
  --description "Salta ASDD. Solo el responsable. Último recurso. Exige '## Motivo del bypass'."
```

**Desde la web**
1. Repositorio → pestaña **Issues** → botón **Labels** (o `https://github.com/<owner>/<repo>/labels`).
2. **New label**.
3. Label name: `asdd-bypass` · Description: la de arriba · Color: `#B60205`.
4. **Create label**.

## 2. Usarlo (cada vez que haga falta)

**Con GitHub CLI**
```bash
git checkout -b hotfix/<nombre>
git commit --allow-empty -m "Bypass ASDD: <motivo corto>"   # hace falta un commit para abrir el PR
git push -u origin hotfix/<nombre>
gh pr create --draft --title "Hotfix: <nombre>" --body-file .github/pull_request_template.md
gh pr edit --add-label asdd-bypass
# Edita la descripción del PR y rellena "## Motivo del bypass" (web o: gh pr edit --body-file motivo.md)
```
Desde ese momento, el hook local (máximo 5 minutos de caché; borra `.asdd/bypass-cache.json`
para forzar) y la CI dejan pasar esa rama.

**Desde la web**
1. Crea la rama y ábrele un PR (puede ser borrador).
2. En la barra lateral derecha del PR, **Labels** → ⚙ → marca `asdd-bypass`.
3. Edita la descripción y rellena `## Motivo del bypass`.

## 3. El motivo (obligatorio)

La CI falla si, con el label puesto, la sección no existe, está vacía o solo tiene el comentario
de la plantilla. Debe explicar **por qué no había alternativa** al flujo normal. Ejemplo:

```markdown
## Motivo del bypass
Webhook de pagos de cliente X caído en producción desde las 09:10. Hotfix de una línea en
src/webhooks/stripe.ts para restaurar el servicio; no había margen para SPEC y PLAN.
```

## 4. Retirarlo

Quita el label del PR (`gh pr edit --remove-label asdd-bypass` o desde la web). La CI se vuelve
a ejecutar automáticamente y exige de nuevo el flujo completo. Borra `.asdd/bypass-cache.json`
para que el hook local también lo note al momento.
