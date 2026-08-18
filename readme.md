# **Smash Amiibo Editor** - Traducción al Español

---

## ⚠️ Nota sobre esta traducción / Note about this translation

**[ES]** Esta es una traducción no oficial al español del proyecto original **Smash Amiibo Editor**, creada por la comunidad para facilitar su uso a jugadores hispanohablantes. **NO es una versión oficial** y no está afiliada ni respaldada por los autores originales. Todos los créditos, derechos y méritos del programa pertenecen exclusivamente a sus creadores originales: **MiDe** y **jozz**.

Repositorio oficial: https://github.com/jozz024/smash-amiibo-editor

**[EN]** This is an unofficial Spanish translation of the original project **Smash Amiibo Editor**, created by the community to make it easier for Spanish-speaking players to use. **It is NOT an official version** and is not affiliated with or endorsed by the original authors. All credits, rights, and recognition for the program belong exclusively to its original creators: **MiDe** and **jozz**.

Official repository: https://github.com/jozz024/smash-amiibo-editor

---

### *AVISO: No uses amiibos editados en torneos a menos que el organizador (TO) los permita explícitamente. Hacerlo puede resultar en un ban permanente del torneo.*

## [Haz clic aquí para descargar](https://github.com/jozz024/smash-amiibo-editor/releases/latest/download/SmashAmiiboEditor.zip)

## Claves de Encriptación

Se necesitan claves de encriptación/desencriptación para editar amiibos. Smash Amiibo Editor soporta tanto `key_retail.bin` como `locked-secret.bin` + `unfixed-info.bin`. Colócalos en la carpeta `resources` o selecciónalos al iniciar el programa.
**Debes obtener las claves por tu cuenta, nosotros no las proporcionaremos.**

## Regiones

Smash Amiibo Editor usa un archivo `.json` compilado con el conocimiento más reciente sobre amiibos para facilitar tu edición. Proporcionamos un archivo de regiones con la investigación más actualizada sobre amiibos.

Si quieres crear tu propio JSON de regiones (o añadir datos al final de uno existente), usa [esta herramienta](https://github.com/jozz024/sae-region-maker/releases/latest).

También tiene compatibilidad con versiones anteriores del formato `regions.txt` de [amiibox](https://github.com/fudgepop01/amiibox), pero se recomienda encarecidamente usar el que nosotros proporcionamos.

## Marca de Agua

Smash Amiibo Editor incluye una marca de agua en el amiibo.
Solo se activa cuando editas secciones de datos de entrenamiento, así que si solo quieres editar tus espíritus, asegúrate de no tocar ninguna de esas secciones.
Para validar cualquier amiibo editado por esta aplicación, usa el [validador de amiibos](https://fudgepop01.github.io/amiibox/).

## Plantillas

Las plantillas son una nueva herramienta para ayudar en la investigación de amiibos. Se pueden usar para aplicar valores preconfigurados a secciones específicas de un archivo de regiones. Las plantillas incluidas son: `max`, `min` y `default`. `max` maximiza todos los valores, `min` minimiza todos los valores, y `default` establece todos los valores en lo que se considera valores "por defecto". ¡También puedes crear tus propias plantillas!

## Mii

Con la versión 1.6.0 de Smash Amiibo Editor, ahora soportamos el registro de amiibos y la exportación/carga de tus miis. Para exportar tu mii, simplemente carga un amiibo, ve a la pestaña `Mii`, y haz clic en `Exportar Mii`. Para cambiar el mii de un amiibo, carga el amiibo, ve a la pestaña `Mii`, haz clic en `Cargar Mii`, y selecciona el archivo mii previamente exportado.

## Documento de Investigación de Amiibos

Los archivos de regiones incluidos en las versiones de Smash Amiibo Editor están fuertemente basados en los datos de [este documento](https://docs.google.com/document/d/1L3c-QKr46ATTSxaicPHNFq5uW-uRytVViPRvdM93IQo/). Envía un DM a `@MiDe#9934` / `mide.` en Discord si tienes preguntas, comentarios o inquietudes sobre este proyecto, o si tienes nueva investigación que añadir.

## Créditos

Desarrollado por [MiDe](https://github.com/MiDe-S) y [jozz](https://github.com/jozz024).

Agradecimientos especiales a untitled1991 y [Ske](https://twitter.com/floofstrid).

**Traducción al español:** Realizada por la comunidad.

## Compilación

### Usa PyInstaller 5.13.2 para evitar falsos positivos de Windows Defender

Para compilar la aplicación, debes tener PyInstaller + las dependencias de `requirements.txt` instaladas.

1. `pyinstaller --onefile resources/update.py`
2. Mueve `update.exe` desde `dist` a la carpeta `resources`
3. `pyinstaller main.spec`
