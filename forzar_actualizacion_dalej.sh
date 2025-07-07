#!/bin/bash
# Script para forzar actualización completa en PythonAnywhere

echo "=== FORZAR ACTUALIZACIÓN COMPLETA PYTHONANYWHERE ==="
echo "1. Descargando cambios del repositorio..."
git fetch --all

echo "2. Verificando commits disponibles..."
git log --oneline -3 origin/main

echo "3. Forzando actualización local..."
git reset --hard origin/main

echo "4. Verificando archivos críticos..."
ls -la | grep -E "(verificacion|resumen|instrucciones)"

echo "5. Limpiando cache de git..."
git clean -fd

echo "6. Estado final:"
git status

echo "=== ACTUALIZACIÓN COMPLETA ==="
