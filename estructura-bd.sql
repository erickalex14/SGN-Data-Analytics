-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: zephyr.proxy.rlwy.net    Database: railway
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cas`
--

DROP TABLE IF EXISTS `cas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cas` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `prefijo` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Prefijo único para códigos de órdenes del CAS',
  `marca` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `correo` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ciudad` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contacto` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notas` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cas_nombre` (`nombre`),
  KEY `idx_cas_activo` (`activo`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `identificacion` varchar(13) NOT NULL,
  `numero_contacto` varchar(10) NOT NULL,
  `correo` varchar(50) DEFAULT NULL,
  `direccion_clientes` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `identificacion` (`identificacion`)
) ENGINE=InnoDB AUTO_INCREMENT=1198 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `credencialesequipo`
--

DROP TABLE IF EXISTS `credencialesequipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credencialesequipo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipo_id` int NOT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  `contrasena` mediumtext NOT NULL,
  `es_patron` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `equipo_id` (`equipo_id`),
  CONSTRAINT `credencialesequipo_ibfk_1` FOREIGN KEY (`equipo_id`) REFERENCES `equipos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `empresas`
--

DROP TABLE IF EXISTS `empresas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ruc` varchar(13) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `correo` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion_empresa` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_empresas_ruc` (`ruc`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipos`
--

DROP TABLE IF EXISTS `equipos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(50) NOT NULL,
  `tipo_servicio_id` int DEFAULT NULL,
  `tipo_servicio_texto` varchar(100) DEFAULT NULL,
  `marca` varchar(50) NOT NULL,
  `modelo` varchar(50) NOT NULL,
  `serie` varchar(100) NOT NULL,
  `contrasena_equipo` varchar(100) DEFAULT NULL,
  `falla` text,
  `observacion` text,
  `fecha_facturacion` date DEFAULT NULL,
  `producto_inventario_codigo` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_equipos_tipo_servicio` (`tipo_servicio_id`),
  KEY `idx_eq_prod_inv` (`producto_inventario_codigo`),
  CONSTRAINT `fk_equipos_tipo_servicio` FOREIGN KEY (`tipo_servicio_id`) REFERENCES `tiposservicio` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1644 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equiposseries`
--

DROP TABLE IF EXISTS `equiposseries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equiposseries` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `equipo_id` int unsigned NOT NULL,
  `serie` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `orden` tinyint unsigned NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_equipo_id` (`equipo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1910 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gruposacceso`
--

DROP TABLE IF EXISTS `gruposacceso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gruposacceso` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_superadmin` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_grupo_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `informefotos`
--

DROP TABLE IF EXISTS `informefotos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `informefotos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `informe_id` int NOT NULL,
  `foto_data` longblob,
  `caption` varchar(255) DEFAULT NULL,
  `nombre_archivo` varchar(255) DEFAULT NULL,
  `tipo_mime` varchar(100) DEFAULT 'image/jpeg',
  `orden_foto` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `informe_id` (`informe_id`),
  CONSTRAINT `informefotos_ibfk_1` FOREIGN KEY (`informe_id`) REFERENCES `informes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=362 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `informes`
--

DROP TABLE IF EXISTS `informes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `informes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `orden_id` int NOT NULL,
  `tecnico_id` int NOT NULL,
  `antecedentes` longtext,
  `proceso` longtext,
  `conclusion` longtext,
  `recomendaciones` longtext,
  `estado_equipo` varchar(60) DEFAULT 'Operativo',
  `fecha_informe` date NOT NULL DEFAULT (curdate()),
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `presupuesto_json` mediumtext,
  PRIMARY KEY (`id`),
  KEY `orden_id` (`orden_id`),
  KEY `tecnico_id` (`tecnico_id`),
  CONSTRAINT `informes_ibfk_2` FOREIGN KEY (`tecnico_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1170 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `listascompra`
--

DROP TABLE IF EXISTS `listascompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `listascompra` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nro_lista` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `creado_por` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `creado_por_id` int DEFAULT NULL,
  `fecha_creacion` date NOT NULL,
  `estado` enum('Pendiente','Completada','Cancelada') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pendiente',
  `observacion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marcas`
--

DROP TABLE IF EXISTS `marcas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marcas` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `migrations`
--

DROP TABLE IF EXISTS `migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `migrations` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `migration` varchar(255) NOT NULL,
  `batch` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notificaciones`
--

DROP TABLE IF EXISTS `notificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int unsigned NOT NULL,
  `tipo` enum('nc_solicitud','nc_aprobada','nc_rechazada') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nc_id` int unsigned DEFAULT NULL,
  `orden_id` int unsigned DEFAULT NULL,
  `nro_orden` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_usuario_leida` (`usuario_id`,`leida`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=832 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orden_empresa_tecnicos`
--

DROP TABLE IF EXISTS `orden_empresa_tecnicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_empresa_tecnicos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `orden_empresa_id` int unsigned NOT NULL,
  `tecnico_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_oet_orden` (`orden_empresa_id`),
  KEY `idx_oet_tecnico` (`tecnico_id`),
  CONSTRAINT `orden_empresa_tecnicos_orden_empresa_id_foreign` FOREIGN KEY (`orden_empresa_id`) REFERENCES `ordenesempresas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orden_empresa_tecnicos_tecnico_id_foreign` FOREIGN KEY (`tecnico_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orden_repuestos`
--

DROP TABLE IF EXISTS `orden_repuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_repuestos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `orden_id` int unsigned NOT NULL,
  `repuesto_id` int unsigned NOT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orden_id` (`orden_id`),
  KEY `repuesto_id` (`repuesto_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ordenes`
--

DROP TABLE IF EXISTS `ordenes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nro_orden` varchar(20) DEFAULT NULL,
  `nro_factura` varchar(20) DEFAULT NULL,
  `nro_factura_2` varchar(17) DEFAULT NULL,
  `motivo_ingreso` enum('Validacion de Garantia','Servicio Cliente Externo','Servicio Tecnico','Servicios a Empresas') NOT NULL DEFAULT 'Servicio Cliente Externo',
  `nro_sucursal_cliente` char(5) DEFAULT NULL,
  `cliente_id` int NOT NULL,
  `equipo_id` int NOT NULL,
  `tecnico_id` int NOT NULL,
  `sucursal_id` int NOT NULL,
  `fecha_de_ingreso` datetime DEFAULT CURRENT_TIMESTAMP,
  `estado_orden` varchar(50) DEFAULT 'Pendiente',
  `estado_repuesto` varchar(50) DEFAULT 'No requerido',
  `estado_garantia` varchar(20) DEFAULT NULL,
  `garantia_tipo` enum('propia','externa') DEFAULT NULL,
  `garantia_cas` varchar(100) DEFAULT NULL,
  `cas_id` int unsigned DEFAULT NULL,
  `cas_fecha_envio` date DEFAULT NULL,
  `cas_fecha_retorno` date DEFAULT NULL,
  `cas_numero_caso` varchar(60) DEFAULT NULL,
  `ingresado_por` int DEFAULT NULL,
  `fecha_prometido` date DEFAULT NULL,
  `modificado_por` int DEFAULT NULL,
  `fecha_modificacion` datetime DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `fecha_finalizacion` datetime DEFAULT NULL,
  `valor_estandar_id` int DEFAULT NULL,
  `repuesto_inventario_id` int DEFAULT NULL COMMENT 'FK opcional a ProductosInventario.id ΓÇö repuesto asignado a la orden',
  `observacion` text,
  `tipo_servicio_id` int unsigned DEFAULT NULL,
  `tipo_servicio_texto` varchar(255) DEFAULT NULL,
  `fecha_facturacion` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nro_orden` (`nro_orden`),
  KEY `cliente_id` (`cliente_id`),
  KEY `equipo_id` (`equipo_id`),
  KEY `tecnico_id` (`tecnico_id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `fk_ingresado_por` (`ingresado_por`),
  KEY `fk_modificado_por` (`modificado_por`),
  KEY `fk_ordenes_valor_estandar` (`valor_estandar_id`),
  KEY `idx_repuesto_inventario_id` (`repuesto_inventario_id`),
  CONSTRAINT `fk_ordenes_valor_estandar` FOREIGN KEY (`valor_estandar_id`) REFERENCES `preciosestandar` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `ordenes_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
  CONSTRAINT `ordenes_ibfk_2` FOREIGN KEY (`equipo_id`) REFERENCES `equipos` (`id`),
  CONSTRAINT `ordenes_ibfk_3` FOREIGN KEY (`tecnico_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ordenes_ibfk_4` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `ordenes_ibfk_5` FOREIGN KEY (`ingresado_por`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL,
  CONSTRAINT `ordenes_ibfk_6` FOREIGN KEY (`modificado_por`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=1566 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ordenesempresas`
--

DROP TABLE IF EXISTS `ordenesempresas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenesempresas` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nro_orden` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_id` int unsigned NOT NULL,
  `subtipo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nro_sucursal_cliente` char(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipo_id` int unsigned DEFAULT NULL,
  `tipo_servicio` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nro_ticket` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tecnico_id` int unsigned NOT NULL,
  `sucursal_id` int unsigned NOT NULL,
  `cas_id` int unsigned DEFAULT NULL,
  `ingresado_por` int unsigned DEFAULT NULL,
  `fecha_prometido` date DEFAULT NULL,
  `estado` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Abierta',
  `valor_hora` decimal(10,2) DEFAULT NULL,
  `horas_trabajadas` decimal(8,2) DEFAULT NULL,
  `fecha_ingreso` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nro_orden` (`nro_orden`),
  KEY `idx_empresa` (`empresa_id`),
  KEY `idx_equipo` (`equipo_id`),
  KEY `idx_tecnico` (`tecnico_id`),
  KEY `idx_sucursal` (`sucursal_id`),
  KEY `ordenesempresas_cas_id_foreign` (`cas_id`),
  CONSTRAINT `ordenesempresas_cas_id_foreign` FOREIGN KEY (`cas_id`) REFERENCES `cas` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=40078 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permisosgrupo`
--

DROP TABLE IF EXISTS `permisosgrupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisosgrupo` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `grupo_id` int unsigned NOT NULL,
  `modulo` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `accion` enum('ver','crear','editar','eliminar') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `permitido` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_permiso` (`grupo_id`,`modulo`,`accion`),
  KEY `idx_permisos_grupo_modulo` (`grupo_id`,`modulo`,`accion`),
  CONSTRAINT `fk_pg_grupo` FOREIGN KEY (`grupo_id`) REFERENCES `gruposacceso` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=718 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permisosusuario`
--

DROP TABLE IF EXISTS `permisosusuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisosusuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `modulo` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `accion` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ver',
  `permitido` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_usuario_mod_acc` (`usuario_id`,`modulo`,`accion`),
  KEY `idx_usuario` (`usuario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `preciosestandar`
--

DROP TABLE IF EXISTS `preciosestandar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preciosestandar` (
  `id` int NOT NULL AUTO_INCREMENT,
  `servicio` varchar(200) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `preciosorden`
--

DROP TABLE IF EXISTS `preciosorden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preciosorden` (
  `id` int NOT NULL AUTO_INCREMENT,
  `orden_id` int NOT NULL,
  `precio_estandar_id` int DEFAULT NULL,
  `servicio` varchar(200) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `orden_id` (`orden_id`),
  KEY `precio_estandar_id` (`precio_estandar_id`),
  CONSTRAINT `preciosorden_ibfk_1` FOREIGN KEY (`orden_id`) REFERENCES `ordenes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `preciosorden_ibfk_2` FOREIGN KEY (`precio_estandar_id`) REFERENCES `preciosestandar` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `preordenes`
--

DROP TABLE IF EXISTS `preordenes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preordenes` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `orden_id` int unsigned DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `nro_preorden` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sucursal_id` int unsigned NOT NULL,
  `nombres` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellidos` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `identificacion` varchar(13) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nro_factura` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `codigo_producto` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `desc_producto` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `marca_producto` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tipo_producto` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detalle_equipo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `foto_1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `foto_2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `foto_3` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `foto_4` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` enum('pendiente','atendida','cancelada') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'pendiente',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `nro_sucursal_cliente` smallint unsigned DEFAULT NULL COMMENT 'FK a SucursalesCliente.id',
  `ciudad_procedencia` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_facturacion` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nro_preorden` (`nro_preorden`),
  KEY `idx_nro_sucursal_cliente` (`nro_sucursal_cliente`),
  KEY `idx_preordenes_orden_id` (`orden_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `productosinventario`
--

DROP TABLE IF EXISTS `productosinventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productosinventario` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `marca_id` int unsigned NOT NULL,
  `tipo_dispositivo_id` int DEFAULT NULL,
  `tipo_dispositivo_codigo` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_codigo` (`codigo`),
  KEY `fk_pi_marca` (`marca_id`),
  KEY `fk_prod_tipo_dispositivo` (`tipo_dispositivo_id`),
  KEY `idx_prod_codigo` (`codigo`),
  CONSTRAINT `fk_pi_marca` FOREIGN KEY (`marca_id`) REFERENCES `marcas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_prod_tipo_dispositivo` FOREIGN KEY (`tipo_dispositivo_id`) REFERENCES `tiposdispositivo` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=781 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `repuestos`
--

DROP TABLE IF EXISTS `repuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repuestos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nro_parte` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nombre` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `marca_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tipo_dispositivo_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `modificado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `stock` int NOT NULL DEFAULT '0',
  `costo` decimal(10,2) NOT NULL DEFAULT '0.00',
  `bodega` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=2086 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rol` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rol` (`rol`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `solicitudesnc`
--

DROP TABLE IF EXISTS `solicitudesnc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudesnc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nro_solicitud` varchar(20) NOT NULL,
  `orden_id` int NOT NULL,
  `fecha_solicitud` date NOT NULL,
  `asunto` varchar(200) NOT NULL,
  `detalles` text NOT NULL,
  `nombre_admin` varchar(100) DEFAULT NULL,
  `motivo_rechazo` text,
  `tecnico_nombre` varchar(100) NOT NULL,
  `tecnico_id` int NOT NULL,
  `estado` enum('Pendiente','Aprobada','Rechazada') NOT NULL DEFAULT 'Pendiente',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nro_solicitud` (`nro_solicitud`),
  UNIQUE KEY `orden_id` (`orden_id`),
  KEY `tecnico_id` (`tecnico_id`),
  CONSTRAINT `solicitudesnc_ibfk_1` FOREIGN KEY (`orden_id`) REFERENCES `ordenes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `solicitudesnc_ibfk_2` FOREIGN KEY (`tecnico_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=230 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `solicitudesrepuesto`
--

DROP TABLE IF EXISTS `solicitudesrepuesto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudesrepuesto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nro_solicitud` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `orden_id` int NOT NULL,
  `tecnico_id` int NOT NULL,
  `tecnico_nombre` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `repuesto_nombre` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `nro_parte` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nro_parte_inv_id` int DEFAULT NULL,
  `repuesto_codigo` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `repuesto_inv_id` int DEFAULT NULL,
  `link_compra` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `estado` enum('Pendiente','Aprobada','Rechazada') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pendiente',
  `motivo_rechazo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `aprobado_por` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `repuesto_id` int DEFAULT NULL,
  `lista_compra_id` int DEFAULT NULL,
  `fecha_solicitud` date NOT NULL,
  `fecha_gestion` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_orden` (`orden_id`),
  KEY `idx_estado` (`estado`),
  KEY `idx_tecnico` (`tecnico_id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sucursales`
--

DROP TABLE IF EXISTS `sucursales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sucursales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nro_sucursal` int NOT NULL,
  `ciudad` varchar(100) NOT NULL,
  `secuencial` varchar(10) NOT NULL,
  `nro_base` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nro_sucursal` (`nro_sucursal`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sucursalescliente`
--

DROP TABLE IF EXISTS `sucursalescliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sucursalescliente` (
  `id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `codigo` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'C├│digo interno (N001, E001, 999)',
  `numero` smallint unsigned NOT NULL COMMENT 'N├║mero de sucursal',
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Nombre de la sucursal',
  `provincia` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Provincia del Ecuador',
  `novitec_sucursal` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Sucursal Novitec responsable: UIO / GYE / MTA',
  `activa` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idx_provincia` (`provincia`),
  KEY `idx_novitec_sucursal` (`novitec_sucursal`),
  KEY `idx_activa` (`activa`)
) ENGINE=InnoDB AUTO_INCREMENT=160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tiposdispositivo`
--

DROP TABLE IF EXISTS `tiposdispositivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tiposdispositivo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tipo_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=292 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tiposservicio`
--

DROP TABLE IF EXISTS `tiposservicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tiposservicio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL DEFAULT '0.00',
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuariocas`
--

DROP TABLE IF EXISTS `usuariocas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuariocas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `cas_id` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuario_cas` (`usuario_id`,`cas_id`),
  KEY `fk_uc_cas` (`cas_id`),
  KEY `idx_uc_usuario` (`usuario_id`),
  CONSTRAINT `fk_uc_cas` FOREIGN KEY (`cas_id`) REFERENCES `cas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_uc_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario` char(10) NOT NULL,
  `clave` varchar(12) NOT NULL,
  `nombre_tecnico` varchar(100) NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `correo_tec` varchar(100) DEFAULT NULL,
  `acceso_nc` tinyint(1) NOT NULL DEFAULT '0',
  `rol_id` int NOT NULL,
  `sucursal_id` int NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `session_token` varchar(64) DEFAULT NULL,
  `grupo_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario` (`usuario`),
  KEY `rol_id` (`rol_id`),
  KEY `sucursal_id` (`sucursal_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuariosucursales`
--

DROP TABLE IF EXISTS `usuariosucursales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuariosucursales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `sucursal_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuario_sucursal` (`usuario_id`,`sucursal_id`),
  KEY `fk_us_sucursal` (`sucursal_id`),
  KEY `idx_us_usuario` (`usuario_id`),
  CONSTRAINT `fk_us_sucursal` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_us_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `vista_ordenes`
--

DROP TABLE IF EXISTS `vista_ordenes`;
/*!50001 DROP VIEW IF EXISTS `vista_ordenes`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_ordenes` AS SELECT 
 1 AS `orden_id`,
 1 AS `nro_orden`,
 1 AS `tipo_orden`,
 1 AS `estado_orden`,
 1 AS `estado_repuesto`,
 1 AS `estado_garantia`,
 1 AS `motivo_ingreso`,
 1 AS `fecha_de_ingreso`,
 1 AS `fecha_prometido`,
 1 AS `fecha_entrega`,
 1 AS `nro_factura`,
 1 AS `nro_factura_2`,
 1 AS `nro_sucursal_cliente`,
 1 AS `tecnico_id`,
 1 AS `sucursal_id`,
 1 AS `ingresado_por`,
 1 AS `cliente_id`,
 1 AS `empresa_id`,
 1 AS `equipo_id`,
 1 AS `cliente`,
 1 AS `nombres`,
 1 AS `apellidos`,
 1 AS `identificacion`,
 1 AS `numero_contacto`,
 1 AS `correo`,
 1 AS `direccion`,
 1 AS `tipo`,
 1 AS `marca`,
 1 AS `modelo`,
 1 AS `serie`,
 1 AS `falla`,
 1 AS `observacion`,
 1 AS `fecha_facturacion`,
 1 AS `tecnico`,
 1 AS `sucursal`,
 1 AS `fecha_de_ingreso_fmt`,
 1 AS `fecha_prometido_fmt`,
 1 AS `fecha_entrega_fmt`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'railway'
--

--
-- Dumping routines for database 'railway'
--

--
-- Final view structure for view `vista_ordenes`
--

/*!50001 DROP VIEW IF EXISTS `vista_ordenes`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_ordenes` AS select `o`.`id` AS `orden_id`,`o`.`nro_orden` AS `nro_orden`,'personal' AS `tipo_orden`,`o`.`estado_orden` AS `estado_orden`,`o`.`estado_repuesto` AS `estado_repuesto`,`o`.`estado_garantia` AS `estado_garantia`,`o`.`motivo_ingreso` AS `motivo_ingreso`,`o`.`fecha_de_ingreso` AS `fecha_de_ingreso`,`o`.`fecha_prometido` AS `fecha_prometido`,`o`.`fecha_entrega` AS `fecha_entrega`,`o`.`nro_factura` AS `nro_factura`,`o`.`nro_factura_2` AS `nro_factura_2`,`o`.`nro_sucursal_cliente` AS `nro_sucursal_cliente`,`o`.`tecnico_id` AS `tecnico_id`,`o`.`sucursal_id` AS `sucursal_id`,`o`.`ingresado_por` AS `ingresado_por`,`o`.`cliente_id` AS `cliente_id`,NULL AS `empresa_id`,`o`.`equipo_id` AS `equipo_id`,concat(`c`.`nombres`,' ',`c`.`apellidos`) AS `cliente`,`c`.`nombres` AS `nombres`,`c`.`apellidos` AS `apellidos`,`c`.`identificacion` AS `identificacion`,`c`.`numero_contacto` AS `numero_contacto`,`c`.`correo` AS `correo`,`c`.`direccion_clientes` AS `direccion`,`e`.`tipo` AS `tipo`,`e`.`marca` AS `marca`,`e`.`modelo` AS `modelo`,`e`.`serie` AS `serie`,`e`.`falla` AS `falla`,`e`.`observacion` AS `observacion`,date_format(`e`.`fecha_facturacion`,'%Y-%m-%d') AS `fecha_facturacion`,`u`.`nombre_tecnico` AS `tecnico`,`s`.`ciudad` AS `sucursal`,date_format(`o`.`fecha_de_ingreso`,'%d/%m/%Y %H:%i') AS `fecha_de_ingreso_fmt`,date_format(`o`.`fecha_prometido`,'%d/%m/%Y') AS `fecha_prometido_fmt`,date_format(`o`.`fecha_entrega`,'%d/%m/%Y') AS `fecha_entrega_fmt` from ((((`ordenes` `o` join `clientes` `c` on((`o`.`cliente_id` = `c`.`id`))) join `equipos` `e` on((`o`.`equipo_id` = `e`.`id`))) join `usuarios` `u` on((`o`.`tecnico_id` = `u`.`id`))) join `sucursales` `s` on((`o`.`sucursal_id` = `s`.`id`))) union all select `oe`.`id` AS `orden_id`,(`oe`.`nro_orden` collate utf8mb4_0900_ai_ci) AS `nro_orden`,'empresa' AS `tipo_orden`,(`oe`.`estado` collate utf8mb4_0900_ai_ci) AS `estado_orden`,'No requerido' AS `estado_repuesto`,NULL AS `estado_garantia`,(concat('Empresa · ',`oe`.`subtipo`) collate utf8mb4_0900_ai_ci) AS `motivo_ingreso`,`oe`.`fecha_ingreso` AS `fecha_de_ingreso`,`oe`.`fecha_prometido` AS `fecha_prometido`,NULL AS `fecha_entrega`,NULL AS `nro_factura`,NULL AS `nro_factura_2`,(`oe`.`nro_sucursal_cliente` collate utf8mb4_0900_ai_ci) AS `nro_sucursal_cliente`,`oe`.`tecnico_id` AS `tecnico_id`,`oe`.`sucursal_id` AS `sucursal_id`,`oe`.`ingresado_por` AS `ingresado_por`,NULL AS `cliente_id`,`oe`.`empresa_id` AS `empresa_id`,`oe`.`equipo_id` AS `equipo_id`,(`emp`.`nombre` collate utf8mb4_0900_ai_ci) AS `cliente`,(`emp`.`nombre` collate utf8mb4_0900_ai_ci) AS `nombres`,'' AS `apellidos`,(`emp`.`ruc` collate utf8mb4_0900_ai_ci) AS `identificacion`,(`emp`.`telefono` collate utf8mb4_0900_ai_ci) AS `numero_contacto`,(`emp`.`correo` collate utf8mb4_0900_ai_ci) AS `correo`,(`emp`.`direccion_empresa` collate utf8mb4_0900_ai_ci) AS `direccion`,`e`.`tipo` AS `tipo`,`e`.`marca` AS `marca`,`e`.`modelo` AS `modelo`,`e`.`serie` AS `serie`,(`oe`.`descripcion` collate utf8mb4_0900_ai_ci) AS `falla`,(`oe`.`descripcion` collate utf8mb4_0900_ai_ci) AS `observacion`,NULL AS `fecha_facturacion`,`u`.`nombre_tecnico` AS `tecnico`,`s`.`ciudad` AS `sucursal`,date_format(`oe`.`fecha_ingreso`,'%d/%m/%Y %H:%i') AS `fecha_de_ingreso_fmt`,date_format(`oe`.`fecha_prometido`,'%d/%m/%Y') AS `fecha_prometido_fmt`,NULL AS `fecha_entrega_fmt` from ((((`ordenesempresas` `oe` join `empresas` `emp` on((`oe`.`empresa_id` = `emp`.`id`))) join `equipos` `e` on((`oe`.`equipo_id` = `e`.`id`))) join `usuarios` `u` on((`oe`.`tecnico_id` = `u`.`id`))) join `sucursales` `s` on((`oe`.`sucursal_id` = `s`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-03 12:14:42
