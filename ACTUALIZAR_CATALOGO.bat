@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo      EL TIO FRED - ACTUALIZAR CATALOGO
echo ==========================================
echo.

python ACTUALIZAR_CATALOGO.py
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo actualizar el catalogo.
  echo Verifica que Python este instalado.
  pause
  exit /b 1
)

echo.
echo Catalogo local actualizado correctamente.
echo.

REM PUBLICACION AUTOMATICA:
REM Si esta carpeta ya fue configurada una vez como repositorio Git
REM con un remoto (por ejemplo GitHub Pages), el mismo BAT publicara
REM los cambios en el mismo enlace.
if exist ".git" (
  where git >nul 2>nul
  if not errorlevel 1 (
    echo Publicando cambios en Internet...
    git add .
    git diff --cached --quiet
    if errorlevel 1 (
      git commit -m "Actualizar catalogo"
      if errorlevel 1 (
        echo.
        echo AVISO: No se pudo crear el commit.
        pause
        exit /b 1
      )
      git push
      if errorlevel 1 (
        echo.
        echo AVISO: No se pudo subir el cambio al servidor.
        echo Revisa tu conexion o la configuracion de Git.
        pause
        exit /b 1
      )
      echo.
      echo ==========================================
      echo  CATALOGO PUBLICADO Y ACTUALIZADO
      echo  Usa el mismo enlace de siempre.
      echo ==========================================
    ) else (
      echo No habia cambios nuevos para publicar.
    )
  ) else (
    echo.
    echo AVISO: Git no esta instalado. Solo se actualizo localmente.
  )
) else (
  echo.
  echo NOTA: La publicacion automatica aun no esta configurada.
  echo El catalogo ya esta actualizado en tu PC.
)

echo.
pause
endlocal
