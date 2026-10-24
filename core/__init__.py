import os
import sys

# Permitir importar apps desde el directorio apps
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apps'))

# Soporte para MySQL / MariaDB: preferir mysqlclient nativo si existe, si no usar PyMySQL
try:
    import MySQLdb
except ImportError:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
