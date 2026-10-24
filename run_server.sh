#!/bin/bash
# ==============================================================================
# SCRIPT DE ARRANQUE - SIMULADOR SABER TyT (UNIPUTUMAYO)
# ==============================================================================

echo "======================================================================"
echo "    INICIANDO SIMULADOR SABER TyT - UNIPUTUMAYO"
echo "    Django + MySQL + JWT Security"
echo "======================================================================"

cd "$(dirname "$0")"

# 1. Creación automática de base de datos, tablas y datos semilla (Estilo Hibernate)
echo "--> Inicializando base de datos y esquema automáticamente..."
python3 manage.py setup_database

# 2. Iniciar servidor de desarrollo en el puerto 8000
echo "======================================================================"
echo "--> Servidor listo en: http://127.0.0.1:8000"
echo "--> Presiona Ctrl+C para detener."
echo "======================================================================"

python3 manage.py runserver 0.0.0.0:8000
