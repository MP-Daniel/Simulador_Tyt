import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = 'Crea automáticamente la base de datos MySQL si no existe, ejecuta migraciones y siembra datos iniciales (similar a Hibernate hbm2ddl.auto).'

    def handle(self, *args, **kwargs):
        db_conf = settings.DATABASES['default']
        engine = db_conf.get('ENGINE', '')

        if 'mysql' in engine:
            dbname = db_conf.get('NAME', 'simulador_saber_tyt')
            user = db_conf.get('USER', 'root')
            password = db_conf.get('PASSWORD', '')
            host = db_conf.get('HOST', '127.0.0.1') or '127.0.0.1'
            port = int(db_conf.get('PORT', 3306) or 3306)

            self.stdout.write(self.style.NOTICE(f"--> [Hibernate-style] Conectando a MySQL en {host}:{port} como '{user}' para verificar base de datos '{dbname}'..."))
            try:
                # Preferir MySQLdb nativo, si no PyMySQL
                try:
                    import MySQLdb
                    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password)
                except ImportError:
                    import pymysql
                    conn = pymysql.connect(host=host, port=port, user=user, password=password)

                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.close()
                self.stdout.write(self.style.SUCCESS(f"✓ Base de datos '{dbname}' verificada/creada exitosamente en MySQL."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Aviso al verificar base de datos en MySQL: {e}"))

        self.stdout.write(self.style.NOTICE("--> Ejecutando migraciones automáticas (creación de tablas)..."))
        call_command('migrate', interactive=False)
        self.stdout.write(self.style.SUCCESS("✓ Todas las tablas creadas y sincronizadas en MySQL."))

        self.stdout.write(self.style.NOTICE("--> Sembrando permisos, roles predeterminados y usuarios demo..."))
        call_command('seed_data')
        self.stdout.write(self.style.SUCCESS("✓ Sistema listo para operar."))
