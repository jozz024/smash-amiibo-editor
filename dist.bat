@ECHO OFF
pyinstaller main.spec

mv dist/SmashAmiiboEditor.exe dist/SmashAmiiboEditor/SmashAmiiboEditor.exe

cp resources/regions.json dist/SmashAmiiboEditor/resources/regions.json

cd dist

cd SmashAmiiboEditor

zip SmashAmiiboEditor.zip SmashAmiiboEditor.exe ./resources/regions.json ./templates/*