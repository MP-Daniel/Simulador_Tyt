/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.20-12.3.3-MariaDB, for osx10.20 (arm64)
--
-- Host: 127.0.0.1    Database: simulador_saber_tyt
-- ------------------------------------------------------
-- Server version	12.3.3-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add content type',4,'add_contenttype'),
(14,'Can change content type',4,'change_contenttype'),
(15,'Can delete content type',4,'delete_contenttype'),
(16,'Can view content type',4,'view_contenttype'),
(17,'Can add session',5,'add_session'),
(18,'Can change session',5,'change_session'),
(19,'Can delete session',5,'delete_session'),
(20,'Can view session',5,'view_session'),
(21,'Can add Permiso',6,'add_permiso'),
(22,'Can change Permiso',6,'change_permiso'),
(23,'Can delete Permiso',6,'delete_permiso'),
(24,'Can view Permiso',6,'view_permiso'),
(25,'Can add Rol',7,'add_rol'),
(26,'Can change Rol',7,'change_rol'),
(27,'Can delete Rol',7,'delete_rol'),
(28,'Can view Rol',7,'view_rol'),
(29,'Can add Usuario',8,'add_usuario'),
(30,'Can change Usuario',8,'change_usuario'),
(31,'Can delete Usuario',8,'delete_usuario'),
(32,'Can view Usuario',8,'view_usuario'),
(33,'Can add Categoría / Competencia',9,'add_categoria'),
(34,'Can change Categoría / Competencia',9,'change_categoria'),
(35,'Can delete Categoría / Competencia',9,'delete_categoria'),
(36,'Can view Categoría / Competencia',9,'view_categoria'),
(37,'Can add Pregunta',10,'add_pregunta'),
(38,'Can change Pregunta',10,'change_pregunta'),
(39,'Can delete Pregunta',10,'delete_pregunta'),
(40,'Can view Pregunta',10,'view_pregunta'),
(41,'Can add Importación de Preguntas',11,'add_importacion'),
(42,'Can change Importación de Preguntas',11,'change_importacion'),
(43,'Can delete Importación de Preguntas',11,'delete_importacion'),
(44,'Can view Importación de Preguntas',11,'view_importacion'),
(45,'Can add Opción de Respuesta',12,'add_opcionrespuesta'),
(46,'Can change Opción de Respuesta',12,'change_opcionrespuesta'),
(47,'Can delete Opción de Respuesta',12,'delete_opcionrespuesta'),
(48,'Can view Opción de Respuesta',12,'view_opcionrespuesta'),
(49,'Can add Cuestionario',13,'add_cuestionario'),
(50,'Can change Cuestionario',13,'change_cuestionario'),
(51,'Can delete Cuestionario',13,'delete_cuestionario'),
(52,'Can view Cuestionario',13,'view_cuestionario'),
(53,'Can add Pregunta de Cuestionario',14,'add_cuestionariopregunta'),
(54,'Can change Pregunta de Cuestionario',14,'change_cuestionariopregunta'),
(55,'Can delete Pregunta de Cuestionario',14,'delete_cuestionariopregunta'),
(56,'Can view Pregunta de Cuestionario',14,'view_cuestionariopregunta'),
(57,'Can add Intento de Evaluación',15,'add_intento'),
(58,'Can change Intento de Evaluación',15,'change_intento'),
(59,'Can delete Intento de Evaluación',15,'delete_intento'),
(60,'Can view Intento de Evaluación',15,'view_intento'),
(61,'Can add Respuesta de Intento',16,'add_respuestaintento'),
(62,'Can change Respuesta de Intento',16,'change_respuestaintento'),
(63,'Can delete Respuesta de Intento',16,'delete_respuestaintento'),
(64,'Can view Respuesta de Intento',16,'view_respuestaintento');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` longtext NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES
(1,'Razonamiento Cuantitativo','Resolución de problemas numéricos, modelado matemático y análisis de datos.',1,'2026-10-24 16:49:31.524951'),
(2,'Lectura Crítica','Comprensión semántica, análisis de argumentos y juicio crítico de textos.',1,'2026-10-24 16:49:31.526509'),
(3,'Competencias Ciudadanas','Conocimiento constitucional, mecanismos de participación y convivencia social.',1,'2026-10-24 16:49:31.527904'),
(4,'Inglés','Comprensión lectora y estructuras gramaticales en lengua extranjera nivel B1.',1,'2026-10-24 16:49:31.529322');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `cuestionario_preguntas`
--

DROP TABLE IF EXISTS `cuestionario_preguntas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuestionario_preguntas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `puntaje` decimal(5,2) NOT NULL,
  `orden` int(10) unsigned NOT NULL CHECK (`orden` >= 0),
  `cuestionario_id` bigint(20) NOT NULL,
  `pregunta_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cuestionario_preguntas_cuestionario_id_pregunta_id_3cb1a1f5_uniq` (`cuestionario_id`,`pregunta_id`),
  KEY `cuestionario_preguntas_pregunta_id_f15db75b_fk_preguntas_id` (`pregunta_id`),
  CONSTRAINT `cuestionario_pregunt_cuestionario_id_9b165101_fk_cuestiona` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`),
  CONSTRAINT `cuestionario_preguntas_pregunta_id_f15db75b_fk_preguntas_id` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuestionario_preguntas`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `cuestionario_preguntas` WRITE;
/*!40000 ALTER TABLE `cuestionario_preguntas` DISABLE KEYS */;
INSERT INTO `cuestionario_preguntas` VALUES
(1,2.50,1,1,1),
(2,2.50,2,1,2),
(3,2.50,3,1,3),
(4,2.50,4,1,4),
(5,2.50,5,1,5);
/*!40000 ALTER TABLE `cuestionario_preguntas` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `cuestionarios`
--

DROP TABLE IF EXISTS `cuestionarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuestionarios` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `fecha_apertura` datetime(6) NOT NULL,
  `fecha_cierre` datetime(6) NOT NULL,
  `tiempo_limite_minutos` int(10) unsigned NOT NULL CHECK (`tiempo_limite_minutos` >= 0),
  `intentos_permitidos` int(10) unsigned NOT NULL CHECK (`intentos_permitidos` >= 0),
  `calificacion_maxima` decimal(5,2) NOT NULL,
  `calificacion_aprobacion` decimal(5,2) NOT NULL,
  `mezclar_preguntas` tinyint(1) NOT NULL,
  `mezclar_respuestas` tinyint(1) NOT NULL,
  `permitir_revision` tinyint(1) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuestionarios`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `cuestionarios` WRITE;
/*!40000 ALTER TABLE `cuestionarios` DISABLE KEYS */;
INSERT INTO `cuestionarios` VALUES
(1,'Simulacro Diagnóstico Saber TyT 2026-II','Evaluación diagnóstica integral de competencias genéricas para estudiantes de Ingeniería de Sistemas.','2026-10-19 16:49:31.564517','2026-11-23 16:49:31.564517',60,2,5.00,3.00,1,1,1,'disponible',1,'2026-10-24 16:49:31.565749','2026-10-24 16:49:31.565754'),
(2,'Simulacro de Competencias Ciudadanas e Inglés','Evaluación programada para próximas fechas. Aún no disponible para presentación.','2026-11-03 16:49:31.564517','2026-11-18 16:49:31.564517',45,1,5.00,3.00,1,1,1,'programado',1,'2026-10-24 16:49:31.574565','2026-10-24 16:49:31.574571'),
(3,'Prueba Piloto Saber TyT (Semestre Anterior)','Examen de práctica del semestre anterior. Cerrado para nuevas presentaciones.','2026-08-25 16:49:31.564517','2026-09-24 16:49:31.564517',30,1,5.00,3.00,0,0,0,'cerrado',1,'2026-10-24 16:49:31.576210','2026-10-24 16:49:31.576216');
/*!40000 ALTER TABLE `cuestionarios` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_usuarios_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_usuarios_id` FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(3,'auth','group'),
(2,'auth','permission'),
(6,'authentication','permiso'),
(7,'authentication','rol'),
(8,'authentication','usuario'),
(9,'banco_preguntas','categoria'),
(11,'banco_preguntas','importacion'),
(12,'banco_preguntas','opcionrespuesta'),
(10,'banco_preguntas','pregunta'),
(4,'contenttypes','contenttype'),
(13,'cuestionarios','cuestionario'),
(14,'cuestionarios','cuestionariopregunta'),
(15,'evaluaciones','intento'),
(16,'evaluaciones','respuestaintento'),
(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2026-10-24 16:48:20.425998'),
(2,'contenttypes','0002_remove_content_type_name','2026-10-24 16:48:20.510716'),
(3,'auth','0001_initial','2026-10-24 16:48:20.783314'),
(4,'auth','0002_alter_permission_name_max_length','2026-10-24 16:48:20.827877'),
(5,'auth','0003_alter_user_email_max_length','2026-10-24 16:48:20.832348'),
(6,'auth','0004_alter_user_username_opts','2026-10-24 16:48:20.836399'),
(7,'auth','0005_alter_user_last_login_null','2026-10-24 16:48:20.840839'),
(8,'auth','0006_require_contenttypes_0002','2026-10-24 16:48:20.842098'),
(9,'auth','0007_alter_validators_add_error_messages','2026-10-24 16:48:20.845693'),
(10,'auth','0008_alter_user_username_max_length','2026-10-24 16:48:20.849290'),
(11,'auth','0009_alter_user_last_name_max_length','2026-10-24 16:48:20.852762'),
(12,'auth','0010_alter_group_name_max_length','2026-10-24 16:48:20.887992'),
(13,'auth','0011_update_proxy_permissions','2026-10-24 16:48:20.892375'),
(14,'auth','0012_alter_user_first_name_max_length','2026-10-24 16:48:20.896064'),
(15,'authentication','0001_initial','2026-10-24 16:48:21.438122'),
(16,'admin','0001_initial','2026-10-24 16:48:21.548330'),
(17,'admin','0002_logentry_remove_auto_add','2026-10-24 16:48:21.559612'),
(18,'admin','0003_logentry_add_action_flag_choices','2026-10-24 16:48:21.568124'),
(19,'banco_preguntas','0001_initial','2026-10-24 16:48:21.830612'),
(20,'cuestionarios','0001_initial','2026-10-24 16:48:21.996807'),
(21,'evaluaciones','0001_initial','2026-10-24 16:48:22.296825'),
(22,'sessions','0001_initial','2026-10-24 16:48:22.349089');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `importaciones`
--

DROP TABLE IF EXISTS `importaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `importaciones` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `archivo_nombre` varchar(255) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `total_filas` int(11) NOT NULL,
  `filas_validas` int(11) NOT NULL,
  `filas_duplicadas` int(11) NOT NULL,
  `filas_error` int(11) NOT NULL,
  `detalles_errores` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`detalles_errores`)),
  `usuario_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `importaciones_usuario_id_dc15351a_fk_usuarios_id` (`usuario_id`),
  CONSTRAINT `importaciones_usuario_id_dc15351a_fk_usuarios_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `importaciones`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `importaciones` WRITE;
/*!40000 ALTER TABLE `importaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `importaciones` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `intentos`
--

DROP TABLE IF EXISTS `intentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `intentos` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `numero_intento` int(10) unsigned NOT NULL CHECK (`numero_intento` >= 0),
  `fecha_inicio` datetime(6) NOT NULL,
  `fecha_fin` datetime(6) DEFAULT NULL,
  `duracion_segundos` int(10) unsigned NOT NULL CHECK (`duracion_segundos` >= 0),
  `puntaje_obtenido` decimal(7,2) NOT NULL,
  `puntaje_total_posible` decimal(7,2) NOT NULL,
  `calificacion` decimal(5,2) NOT NULL,
  `estado_intento` varchar(20) NOT NULL,
  `resultado` varchar(20) NOT NULL,
  `total_preguntas` int(10) unsigned NOT NULL CHECK (`total_preguntas` >= 0),
  `aciertos` int(10) unsigned NOT NULL CHECK (`aciertos` >= 0),
  `errores` int(10) unsigned NOT NULL CHECK (`errores` >= 0),
  `omitidas` int(10) unsigned NOT NULL CHECK (`omitidas` >= 0),
  `cuestionario_id` bigint(20) NOT NULL,
  `estudiante_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `intentos_cuestionario_id_7fe3395c_fk_cuestionarios_id` (`cuestionario_id`),
  KEY `intentos_estudiante_id_c35e3d10_fk_usuarios_id` (`estudiante_id`),
  CONSTRAINT `intentos_cuestionario_id_7fe3395c_fk_cuestionarios_id` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`),
  CONSTRAINT `intentos_estudiante_id_c35e3d10_fk_usuarios_id` FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `intentos`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `intentos` WRITE;
/*!40000 ALTER TABLE `intentos` DISABLE KEYS */;
INSERT INTO `intentos` VALUES
(1,1,'2026-10-24 16:50:15.274792','2026-10-24 16:50:15.303338',300,0.00,12.50,0.00,'finalizado','reprobado',5,0,1,4,1,3),
(2,2,'2026-10-24 16:50:33.769447','2026-10-24 16:50:33.801829',300,5.00,12.50,2.00,'finalizado','reprobado',5,2,0,3,1,3);
/*!40000 ALTER TABLE `intentos` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `opciones_respuesta`
--

DROP TABLE IF EXISTS `opciones_respuesta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `opciones_respuesta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `letra` varchar(5) NOT NULL,
  `texto` longtext NOT NULL,
  `es_correcta` tinyint(1) NOT NULL,
  `orden` int(10) unsigned NOT NULL CHECK (`orden` >= 0),
  `pregunta_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `opciones_respuesta_pregunta_id_letra_94e8ae2b_uniq` (`pregunta_id`,`letra`),
  CONSTRAINT `opciones_respuesta_pregunta_id_04ffd3a3_fk_preguntas_id` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opciones_respuesta`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `opciones_respuesta` WRITE;
/*!40000 ALTER TABLE `opciones_respuesta` DISABLE KEYS */;
INSERT INTO `opciones_respuesta` VALUES
(1,'A','$500',0,1,1),
(2,'B','$540',1,1,1),
(3,'C','$580',0,1,1),
(4,'D','$600',0,1,1),
(5,'V','Verdadero',0,1,2),
(6,'F','Falso',1,1,2),
(7,'A','Acción de Cumplimiento',0,1,3),
(8,'B','Acción Popular',0,1,3),
(9,'C','Acción de Tutela',1,1,3),
(10,'D','Habeas Data',0,1,3),
(11,'A','designs',0,1,4),
(12,'B','design',1,1,4),
(13,'C','designing',0,1,4),
(14,'D','designed',0,1,4),
(15,'A','4 segundos',0,1,5),
(16,'B','6 segundos',0,1,5),
(17,'C','8 segundos',1,1,5),
(18,'D','10 segundos',0,1,5);
/*!40000 ALTER TABLE `opciones_respuesta` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `modulo` varchar(100) NOT NULL,
  `descripcion` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
INSERT INTO `permisos` VALUES
(1,'usuarios.administrar','Administrar Usuarios','Usuarios','Crear, consultar, editar y activar/desactivar cuentas de usuario'),
(2,'roles.administrar','Administrar Roles y Permisos','Roles','Crear, editar, activar/desactivar roles personalizados y asignar permisos'),
(3,'preguntas.gestionar','Gestionar Banco de Preguntas','Banco de Preguntas','Crear, consultar, editar y desactivar reactivos en el banco'),
(4,'preguntas.importar','Importar Preguntas Excel','Banco de Preguntas','Carga masiva y validación fila por fila desde Excel'),
(5,'cuestionarios.gestionar','Configurar Cuestionarios','Cuestionarios','Crear, editar, activar/desactivar cuestionarios y asignar preguntas'),
(6,'cuestionarios.rendir','Presentar Evaluaciones','Cuestionarios','Iniciar, navegar y finalizar intentos de evaluación disponibles'),
(7,'resultados.consultar_propios','Consultar Calificaciones Propias','Resultados','Ver historial y revisiones de sus propios exámenes'),
(8,'resultados.consultar_todos','Consultar Resultados Globales','Resultados','Ver informes, intentos y notas de todos los estudiantes');
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `preguntas`
--

DROP TABLE IF EXISTS `preguntas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `preguntas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(20) NOT NULL,
  `texto_base` longtext DEFAULT NULL,
  `enunciado` longtext NOT NULL,
  `retroalimentacion` longtext NOT NULL,
  `puntaje` decimal(5,2) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `categoria_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `preguntas_categoria_id_4a35bac2_fk_categorias_id` (`categoria_id`),
  CONSTRAINT `preguntas_categoria_id_4a35bac2_fk_categorias_id` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preguntas`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `preguntas` WRITE;
/*!40000 ALTER TABLE `preguntas` DISABLE KEYS */;
INSERT INTO `preguntas` VALUES
(1,'MULTIPLE','En una empresa de software se requiere determinar el costo de producción para el despliegue de infraestructura en la nube.','¿Si un servidor en la nube cuesta $100 al mes, cuánto se pagará en 6 meses con un 10% de descuento?','El costo sin descuento es 6 x $100 = $600. El 10% de 600 es $60. Por tanto, 600 - 60 = $540.',2.50,1,'2026-10-24 16:49:31.530987','2026-10-24 16:49:31.530995',1),
(2,'VERDADERO_FALSO',NULL,'En las pruebas Saber TyT, el componente de lectura crítica evalúa prioritariamente la capacidad de memorizar fechas y nombres de autores.','Es falso. Evalúa la comprensión semántica, la jerarquía de ideas y el análisis de posturas, no la memorización mecánica.',2.50,1,'2026-10-24 16:49:31.539421','2026-10-24 16:49:31.539430',2),
(3,'MULTIPLE','La Constitución Política de Colombia de 1991 consagra derechos fundamentales y mecanismos de protección sumaria.','¿Cuál es el mecanismo judicial expedito para la protección inmediata de los derechos constitucionales fundamentales amenazados o vulnerados?','El artículo 86 de la Constitución consagra la Acción de Tutela para la protección inmediata de derechos fundamentales.',2.50,1,'2026-10-24 16:49:31.543780','2026-10-24 16:49:31.543788',3),
(4,'MULTIPLE',NULL,'Choose the correct sentence to complete the idea: \'Software engineers usually _______ database schemas before writing code.\'','Con el sujeto plural \'Software engineers\', en presente simple se utiliza la forma base \'design\'.',2.50,1,'2026-10-24 16:49:31.551221','2026-10-24 16:49:31.551228',4),
(5,'MULTIPLE','Un algoritmo procesa una lista de N elementos con complejidad cuadrática O(N²).','Si para 10 elementos tarda 2 segundos, ¿cuántos segundos tardará para procesar 20 elementos?','Al duplicar N de 10 a 20, con O(N²) el tiempo se multiplica por 2² = 4. Por ende, 2 s x 4 = 8 segundos.',2.50,1,'2026-10-24 16:49:31.558007','2026-10-24 16:49:31.558015',1);
/*!40000 ALTER TABLE `preguntas` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `respuestas_intento`
--

DROP TABLE IF EXISTS `respuestas_intento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `respuestas_intento` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `es_acierto` tinyint(1) NOT NULL,
  `puntaje_obtenido` decimal(5,2) NOT NULL,
  `marcada_revision` tinyint(1) NOT NULL,
  `respondida_en` datetime(6) NOT NULL,
  `intento_id` bigint(20) NOT NULL,
  `opcion_seleccionada_id` bigint(20) DEFAULT NULL,
  `pregunta_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `respuestas_intento_intento_id_pregunta_id_9adbf8c7_uniq` (`intento_id`,`pregunta_id`),
  KEY `respuestas_intento_opcion_seleccionada__2a44427b_fk_opciones_` (`opcion_seleccionada_id`),
  KEY `respuestas_intento_pregunta_id_27b0822d_fk_preguntas_id` (`pregunta_id`),
  CONSTRAINT `respuestas_intento_intento_id_894394d2_fk_intentos_id` FOREIGN KEY (`intento_id`) REFERENCES `intentos` (`id`),
  CONSTRAINT `respuestas_intento_opcion_seleccionada__2a44427b_fk_opciones_` FOREIGN KEY (`opcion_seleccionada_id`) REFERENCES `opciones_respuesta` (`id`),
  CONSTRAINT `respuestas_intento_pregunta_id_27b0822d_fk_preguntas_id` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `respuestas_intento`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `respuestas_intento` WRITE;
/*!40000 ALTER TABLE `respuestas_intento` DISABLE KEYS */;
INSERT INTO `respuestas_intento` VALUES
(1,0,0.00,0,'2026-10-24 16:50:15.294246',1,NULL,1),
(2,0,0.00,0,'2026-10-24 16:50:15.295988',1,NULL,2),
(3,0,0.00,0,'2026-10-24 16:50:15.298652',1,8,3),
(4,0,0.00,0,'2026-10-24 16:50:15.301172',1,NULL,4),
(5,0,0.00,0,'2026-10-24 16:50:15.302741',1,NULL,5),
(6,0,0.00,0,'2026-10-24 16:50:33.792496',2,NULL,1),
(7,1,2.50,0,'2026-10-24 16:50:33.795186',2,6,2),
(8,1,2.50,0,'2026-10-24 16:50:33.797932',2,9,3),
(9,0,0.00,0,'2026-10-24 16:50:33.799631',2,NULL,4),
(10,0,0.00,0,'2026-10-24 16:50:33.801219',2,NULL,5);
/*!40000 ALTER TABLE `respuestas_intento` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` longtext NOT NULL,
  `es_predeterminado` tinyint(1) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES
(1,'Administrador','Control total del sistema: usuarios, roles, banco, cuestionarios e informes.',1,1,'2026-10-24 16:49:30.612720','2026-10-24 16:49:30.612741'),
(2,'Estudiante','Presentación de cuestionarios habilitados y consulta de notas propias.',1,1,'2026-10-24 16:49:30.616996','2026-10-24 16:49:30.617006'),
(3,'Docente Evaluador','Gestor académico: crea preguntas, cuestionarios e importa desde Excel sin gestionar usuarios.',0,1,'2026-10-24 16:49:30.620008','2026-10-24 16:49:30.620016'),
(4,'Tutor Auxiliar','Rol personalizado para apoyo en reactivos.',0,1,'2026-10-24 16:50:34.042194','2026-10-24 16:50:34.042204');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `roles_permisos`
--

DROP TABLE IF EXISTS `roles_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles_permisos` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rol_id` bigint(20) NOT NULL,
  `permiso_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `roles_permisos_rol_id_permiso_id_daf91080_uniq` (`rol_id`,`permiso_id`),
  KEY `roles_permisos_permiso_id_ff70f233_fk_permisos_id` (`permiso_id`),
  CONSTRAINT `roles_permisos_permiso_id_ff70f233_fk_permisos_id` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id`),
  CONSTRAINT `roles_permisos_rol_id_5daf3c70_fk_roles_id` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles_permisos`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `roles_permisos` WRITE;
/*!40000 ALTER TABLE `roles_permisos` DISABLE KEYS */;
INSERT INTO `roles_permisos` VALUES
(1,1,1),
(2,1,2),
(3,1,3),
(4,1,4),
(5,1,5),
(6,1,6),
(7,1,7),
(8,1,8),
(9,2,6),
(10,2,7),
(11,3,3),
(12,3,4),
(13,3,5),
(14,3,7),
(15,3,8),
(16,4,3),
(17,4,5);
/*!40000 ALTER TABLE `roles_permisos` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `codigo_estudiantil` varchar(50) DEFAULT NULL,
  `programa_academico` varchar(150) NOT NULL,
  `telefono` varchar(30) NOT NULL,
  `rol_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `codigo_estudiantil` (`codigo_estudiantil`),
  KEY `usuarios_rol_id_fa223853_fk_roles_id` (`rol_id`),
  CONSTRAINT `usuarios_rol_id_fa223853_fk_roles_id` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'pbkdf2_sha256$600000$hs6W8MtMWs0vAAAvau0EJS$E1QzR/soYWilUUpleE0NlGWzkKhofVmkEMnAjk9HNnI=','2026-10-24 16:50:33.381375',1,'admin','Administrador','Sistema','admin@uniputumayo.edu.co',1,1,'2026-10-24 16:49:30.622913','ADM-001','Ingeniería de Sistemas','',1),
(2,'pbkdf2_sha256$600000$fFot1Rt07XJHO4zqUQE7ml$jYCobXMlkbDBvTr0Z1WEcqReXxEAW6V9cnCLlIBPuAM=',NULL,0,'docente','Prof. Carlos','Rodríguez','docente@uniputumayo.edu.co',0,1,'2026-10-24 16:49:30.803201','DOC-102','Ingeniería de Sistemas','',3),
(3,'pbkdf2_sha256$600000$Emh23Y3nERZSQXEjSxAE8w$qSjiChWj+te9Sv9jNYLssqtJsi1y6797/XDM9lwKgrA=','2026-10-24 16:50:33.747629',0,'estudiante1','Juan David','Pérez','jperez@uniputumayo.edu.co',0,1,'2026-10-24 16:49:30.983598','SIS-2026-01','Ingeniería de Sistemas','',2),
(4,'pbkdf2_sha256$600000$ogWmMHxjvjzBoAZeIOD8Zt$7aYah9N4GU7K7YIQoy8ED+H+OPRZMO9ygTmdWDURUzc=','2026-10-24 16:50:33.983507',0,'estudiante2','María Paula','Gómez','mgomez@uniputumayo.edu.co',0,1,'2026-10-24 16:49:31.164856','SIS-2026-02','Ingeniería de Sistemas','',2),
(5,'pbkdf2_sha256$600000$BamsfRYJceuVNdPOEFHa70$XtdivBB3u7Z1nJCi056Y77QxYE5JTvEVFHcS4YGF0jg=',NULL,0,'inactivo','Estudiante','Suspendido','inactivo@uniputumayo.edu.co',0,0,'2026-10-24 16:49:31.344465','SIS-2026-99','Ingeniería de Sistemas','',2);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `usuarios_groups`
--

DROP TABLE IF EXISTS `usuarios_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuarios_groups_usuario_id_group_id_a66c5ef3_uniq` (`usuario_id`,`group_id`),
  KEY `usuarios_groups_group_id_18c61092_fk_auth_group_id` (`group_id`),
  CONSTRAINT `usuarios_groups_group_id_18c61092_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `usuarios_groups_usuario_id_1132ca50_fk_usuarios_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_groups`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `usuarios_groups` WRITE;
/*!40000 ALTER TABLE `usuarios_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_groups` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `usuarios_user_permissions`
--

DROP TABLE IF EXISTS `usuarios_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuarios_user_permissions_usuario_id_permission_id_474b33a5_uniq` (`usuario_id`,`permission_id`),
  KEY `usuarios_user_permis_permission_id_af615ca1_fk_auth_perm` (`permission_id`),
  CONSTRAINT `usuarios_user_permis_permission_id_af615ca1_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `usuarios_user_permissions_usuario_id_232fd58d_fk_usuarios_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_user_permissions`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `usuarios_user_permissions` WRITE;
/*!40000 ALTER TABLE `usuarios_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-10-24 11:57:52
