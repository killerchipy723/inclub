-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: inclub_offline
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `cliente_puntos`
--

DROP TABLE IF EXISTS `cliente_puntos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente_puntos` (
  `idcliente` int NOT NULL,
  `puntos` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`idcliente`),
  CONSTRAINT `cliente_puntos_ibfk_1` FOREIGN KEY (`idcliente`) REFERENCES `clientes` (`idclientes`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente_puntos`
--

LOCK TABLES `cliente_puntos` WRITE;
/*!40000 ALTER TABLE `cliente_puntos` DISABLE KEYS */;
/*!40000 ALTER TABLE `cliente_puntos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `idclientes` int NOT NULL AUTO_INCREMENT,
  `apenomb` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `dni` int DEFAULT NULL,
  `cuil` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `correo` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  PRIMARY KEY (`idclientes`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (1,'CONSUMIDOR FINAL',0,'0','alguien@alguien.com','0001-01-01'),(5,'ALDERETE DYLAN EDUARDO',50008803,'20500088037','dalderete303@gmail.com','2000-02-10'),(6,'CARLOS MARTINEZ',544444,'2333232323','alguien@alguien.com','0001-01-01');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes_puntos`
--

DROP TABLE IF EXISTS `clientes_puntos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes_puntos` (
  `idclientes` int NOT NULL,
  `puntos` int DEFAULT '0',
  PRIMARY KEY (`idclientes`),
  CONSTRAINT `clientes_puntos_ibfk_1` FOREIGN KEY (`idclientes`) REFERENCES `clientes` (`idclientes`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes_puntos`
--

LOCK TABLES `clientes_puntos` WRITE;
/*!40000 ALTER TABLE `clientes_puntos` DISABLE KEYS */;
/*!40000 ALTER TABLE `clientes_puntos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jornadas`
--

DROP TABLE IF EXISTS `jornadas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jornadas` (
  `idjornada` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `clave` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `finicio` datetime DEFAULT NULL,
  `ffinal` datetime DEFAULT NULL,
  `estado` varchar(45) COLLATE utf8mb4_general_ci DEFAULT 'Activo',
  PRIMARY KEY (`idjornada`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jornadas`
--

LOCK TABLES `jornadas` WRITE;
/*!40000 ALTER TABLE `jornadas` DISABLE KEYS */;
INSERT INTO `jornadas` VALUES (1,'INCLUB','evento in','2026-01-12 00:00:00','2026-01-12 00:00:00','Finalizado'),(2,'PRUEBA2','inclub26','2026-01-11 00:00:00','2026-01-12 00:00:00','Finalizado'),(3,'BOLICHE','fescande','2026-01-10 00:00:00','2026-01-10 00:00:00','Finalizado'),(4,'BOLICHE','eventin','2026-01-09 00:00:00','2026-01-24 00:00:00','Finalizado'),(6,'EVENTO NAVIDEÑO','event in navidad','2026-01-23 00:00:00','2026-01-10 00:00:00','Finalizado'),(11,'FESTIMIEL','fest2026','2026-01-17 00:00:00','2026-01-18 00:00:00','Finalizado'),(12,'TOMORROW','tomo2026','2026-01-17 00:00:00','2026-01-18 00:00:00','Activo');
/*!40000 ALTER TABLE `jornadas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jornadas_productos`
--

DROP TABLE IF EXISTS `jornadas_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jornadas_productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idjornada` int NOT NULL,
  `idproducto` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idjornada` (`idjornada`,`idproducto`),
  KEY `idproducto` (`idproducto`),
  CONSTRAINT `jornadas_productos_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornadas` (`idjornada`),
  CONSTRAINT `jornadas_productos_ibfk_2` FOREIGN KEY (`idproducto`) REFERENCES `productos` (`idproductos`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jornadas_productos`
--

LOCK TABLES `jornadas_productos` WRITE;
/*!40000 ALTER TABLE `jornadas_productos` DISABLE KEYS */;
INSERT INTO `jornadas_productos` VALUES (1,11,2),(2,11,5),(3,11,6),(4,11,7),(5,11,8),(6,11,10),(7,11,16),(8,12,1),(18,12,2),(19,12,3),(9,12,4),(10,12,6),(20,12,7),(11,12,8),(12,12,9),(13,12,10),(21,12,12),(14,12,13),(15,12,14),(16,12,15),(17,12,17);
/*!40000 ALTER TABLE `jornadas_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jornadas_puntos`
--

DROP TABLE IF EXISTS `jornadas_puntos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jornadas_puntos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idjornada` int NOT NULL,
  `idpunto` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idjornada` (`idjornada`,`idpunto`),
  KEY `idpunto` (`idpunto`),
  CONSTRAINT `jornadas_puntos_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornadas` (`idjornada`),
  CONSTRAINT `jornadas_puntos_ibfk_2` FOREIGN KEY (`idpunto`) REFERENCES `puntos_venta` (`idpunto`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jornadas_puntos`
--

LOCK TABLES `jornadas_puntos` WRITE;
/*!40000 ALTER TABLE `jornadas_puntos` DISABLE KEYS */;
INSERT INTO `jornadas_puntos` VALUES (4,11,1),(5,11,6),(6,11,7),(7,12,1),(8,12,6),(9,12,7);
/*!40000 ALTER TABLE `jornadas_puntos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modopago`
--

DROP TABLE IF EXISTS `modopago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modopago` (
  `idmodopago` int NOT NULL AUTO_INCREMENT,
  `modo` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `estado` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`idmodopago`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modopago`
--

LOCK TABLES `modopago` WRITE;
/*!40000 ALTER TABLE `modopago` DISABLE KEYS */;
INSERT INTO `modopago` VALUES (1,'TRANSFERENCIA','Activo'),(2,'EFECTIVO','Activo');
/*!40000 ALTER TABLE `modopago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `idproductos` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `importe` double DEFAULT NULL,
  `estado` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`idproductos`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'ABSOLUT VODKAS',10000,'Activo'),(2,'AGUA',5000,'Activo'),(3,'CHANDON C/1 SPEED',37000,'Activo'),(4,'CORONA',8000,'Activo'),(5,'DR LEMON',7000,'Activo'),(6,'FERNET',8000,'Activo'),(7,'GANCIA',7000,'Activo'),(8,'GIN',7000,'Activo'),(9,'GASEOSA CHICA',5000,'Activo'),(10,'HEINEKEN',7000,'Activo'),(11,'HOLDMOSER',9000,'Activo'),(12,'RENAIS C/ 1 SPEED',18000,'Activo'),(13,'SMIRNOFF /SKK',9000,'Activo'),(14,'SPEED',6000,'Activo'),(15,'TRAGO COCTEL',8000,'Activo'),(16,'VINO FINO',20000,'Activo'),(17,'VODKA C/ SPEED',8000,'Activo'),(18,'WHISKY HIRAM',12000,'Activo');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `puntos_beneficios`
--

DROP TABLE IF EXISTS `puntos_beneficios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `puntos_beneficios` (
  `idbeneficio` int NOT NULL AUTO_INCREMENT,
  `puntos_requeridos` int NOT NULL,
  `tipo` enum('CONSUMICION','DESCUENTO') COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `valor` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`idbeneficio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `puntos_beneficios`
--

LOCK TABLES `puntos_beneficios` WRITE;
/*!40000 ALTER TABLE `puntos_beneficios` DISABLE KEYS */;
/*!40000 ALTER TABLE `puntos_beneficios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `puntos_venta`
--

DROP TABLE IF EXISTS `puntos_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `puntos_venta` (
  `idpunto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `idequipo` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`idpunto`),
  UNIQUE KEY `idequipo` (`idequipo`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `puntos_venta`
--

LOCK TABLES `puntos_venta` WRITE;
/*!40000 ALTER TABLE `puntos_venta` DISABLE KEYS */;
INSERT INTO `puntos_venta` VALUES (1,'SERVER','127.0.0.1','Activo'),(6,'CAJA 9','192.168.1.44','Activo'),(7,'CAJA8','192.168.1.46','Activo');
/*!40000 ALTER TABLE `puntos_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `idusuarios` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `clave` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `rol` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `estado` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`idusuarios`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Admin','123456','Administrador','Activo'),(3,'CAJA9','1234','Vendedor','Activo'),(4,'CAJA8','1234','Vendedor','Activo');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_puntos`
--

DROP TABLE IF EXISTS `usuarios_puntos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_puntos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idusuario` int NOT NULL,
  `idpunto` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idusuario` (`idusuario`,`idpunto`),
  KEY `idpunto` (`idpunto`),
  CONSTRAINT `usuarios_puntos_ibfk_1` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`idusuarios`),
  CONSTRAINT `usuarios_puntos_ibfk_2` FOREIGN KEY (`idpunto`) REFERENCES `puntos_venta` (`idpunto`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_puntos`
--

LOCK TABLES `usuarios_puntos` WRITE;
/*!40000 ALTER TABLE `usuarios_puntos` DISABLE KEYS */;
INSERT INTO `usuarios_puntos` VALUES (1,3,6),(2,4,7);
/*!40000 ALTER TABLE `usuarios_puntos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `idventa` int NOT NULL AUTO_INCREMENT,
  `idjornada` int NOT NULL,
  `idusuario` int NOT NULL,
  `idpunto` int NOT NULL,
  `idclientes` int DEFAULT NULL,
  `idmodopago` int NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `descuento_total` decimal(10,2) DEFAULT '0.00',
  `fecha_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('OK','ANULADA') COLLATE utf8mb4_general_ci DEFAULT 'OK',
  `observaciones` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `puntos_ganados` int DEFAULT '0',
  `qr_token` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `estado_ticket` enum('VALIDO','USADO','ANULADO') COLLATE utf8mb4_general_ci DEFAULT 'VALIDO',
  PRIMARY KEY (`idventa`),
  KEY `idjornada` (`idjornada`),
  KEY `idusuario` (`idusuario`),
  KEY `idpunto` (`idpunto`),
  KEY `idclientes` (`idclientes`),
  KEY `idmodopago` (`idmodopago`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornadas` (`idjornada`),
  CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`idusuarios`),
  CONSTRAINT `ventas_ibfk_3` FOREIGN KEY (`idpunto`) REFERENCES `puntos_venta` (`idpunto`),
  CONSTRAINT `ventas_ibfk_4` FOREIGN KEY (`idclientes`) REFERENCES `clientes` (`idclientes`),
  CONSTRAINT `ventas_ibfk_5` FOREIGN KEY (`idmodopago`) REFERENCES `modopago` (`idmodopago`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (3,1,4,7,NULL,2,14000.00,0.00,'2026-01-11 14:55:09','OK','',140,'','VALIDO'),(4,1,4,7,NULL,2,25000.00,0.00,'2026-01-11 14:56:43','OK','',250,'','VALIDO'),(5,1,4,7,NULL,1,21000.00,0.00,'2026-01-11 14:59:10','OK','',140,'','VALIDO'),(6,1,4,7,1,2,14000.00,0.00,'2026-01-11 15:10:18','OK','',70,'','VALIDO'),(7,1,4,7,NULL,2,34000.00,0.00,'2026-01-11 16:37:49','OK','',340,'','VALIDO'),(8,1,4,7,NULL,2,28000.00,0.00,'2026-01-11 16:40:55','OK','',280,'','VALIDO'),(9,12,4,7,5,2,45000.00,0.00,'2026-01-12 14:32:49','OK','',450,'','VALIDO'),(10,12,3,6,NULL,2,10000.00,0.00,'2026-01-12 15:07:14','OK','',100,'','VALIDO'),(11,12,3,6,6,2,16000.00,0.00,'2026-01-12 15:08:16','OK','',160,'','VALIDO'),(12,12,3,6,NULL,2,7000.00,0.00,'2026-01-12 15:10:58','OK','',70,'','VALIDO'),(13,12,4,7,1,2,8000.00,0.00,'2026-01-12 15:41:08','OK','',80,'','VALIDO'),(14,12,4,7,1,2,8000.00,0.00,'2026-01-12 15:48:14','OK','',80,'','VALIDO'),(15,12,3,6,1,2,8000.00,0.00,'2026-01-12 15:49:04','OK','',80,'','VALIDO'),(16,12,4,7,1,2,14000.00,0.00,'2026-01-12 16:59:53','OK','',140,'','VALIDO'),(17,12,4,7,1,2,13000.00,0.00,'2026-01-12 17:03:35','OK','',130,'','VALIDO'),(18,12,4,7,1,2,13000.00,0.00,'2026-01-12 17:04:54','OK','',130,'','VALIDO'),(19,12,4,7,1,2,13000.00,0.00,'2026-01-12 17:06:07','OK','',130,'','VALIDO'),(20,12,4,7,1,2,18000.00,0.00,'2026-01-12 17:17:32','OK','',180,'','VALIDO'),(21,12,4,7,1,2,11000.00,0.00,'2026-01-12 17:24:43','OK','',110,'','VALIDO'),(22,12,4,7,5,2,14000.00,0.00,'2026-01-12 17:25:47','OK','',140,'','VALIDO'),(23,12,4,7,5,2,16000.00,0.00,'2026-01-12 22:22:12','OK','',160,'','VALIDO'),(24,12,4,7,6,2,37000.00,0.00,'2026-01-12 22:29:33','OK','',370,'','VALIDO'),(25,12,4,7,5,2,13000.00,0.00,'2026-01-12 22:46:49','OK','',130,'','VALIDO'),(26,12,4,7,5,2,12000.00,0.00,'2026-01-12 22:55:38','OK','',120,'','VALIDO'),(27,12,4,7,5,2,11000.00,0.00,'2026-01-12 22:56:36','OK','',110,'','VALIDO'),(28,12,4,7,6,2,12000.00,0.00,'2026-01-12 23:06:46','OK','',120,'','VALIDO'),(29,12,4,7,5,2,15000.00,0.00,'2026-01-12 23:21:06','OK','',150,'0aba1afea53e4d1993f7208e2131678b','VALIDO'),(30,12,4,7,1,2,7000.00,0.00,'2026-01-12 23:21:30','OK','',70,'1d57360b5d9447eab2df8013d289539c','VALIDO'),(31,12,4,7,1,2,15000.00,0.00,'2026-01-12 23:33:06','OK','',150,'1fff179d3c5240aab9ab67dc66cc1b3f','VALIDO'),(32,12,4,7,1,2,8000.00,0.00,'2026-01-13 21:14:27','OK','',80,'c9ec99e22c27430e8045905a715d053a','VALIDO'),(33,12,4,7,1,2,7000.00,0.00,'2026-01-13 21:15:56','OK','',70,'a2fea95aed304b6895d56f459686eaf1','VALIDO'),(34,12,4,7,1,2,16000.00,0.00,'2026-01-13 21:25:33','OK','',160,'b5e218485baf48f784aa2239345a83c1','VALIDO'),(35,12,4,7,5,2,13000.00,0.00,'2026-01-13 21:31:15','OK','',130,'47b24226b0f343209f936635a8d3cabf','VALIDO'),(36,12,4,7,1,2,14000.00,0.00,'2026-01-13 21:39:21','OK','',140,'9244e65e2cc14ed186ac7ade0611c217','VALIDO'),(37,12,4,7,1,2,37000.00,0.00,'2026-01-13 21:39:58','OK','',370,'af7ab040e96d4d1481194e12fb861692','VALIDO'),(38,12,4,7,6,2,23000.00,0.00,'2026-01-13 22:16:32','OK','',230,'a3200465e00944db82be76cd777b313c','VALIDO'),(39,12,4,7,1,2,8000.00,0.00,'2026-01-13 22:17:50','OK','',80,'6ee28f14dfe54291b0a7568ce06b84e9','VALIDO'),(40,12,4,7,1,2,8000.00,0.00,'2026-01-13 22:18:01','OK','',80,'f774aca922434c3f8765a32f1eab5c9a','VALIDO'),(41,12,4,7,1,2,8000.00,0.00,'2026-01-13 22:18:12','OK','',80,'ccecbf2b2079482a801a8d99d77a5f19','VALIDO'),(42,12,4,7,1,2,27000.00,0.00,'2026-01-13 22:25:53','OK','',270,'7e96108fb3e749ada000a96144be4e20','VALIDO');
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas_detalle`
--

DROP TABLE IF EXISTS `ventas_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas_detalle` (
  `iddetalle` int NOT NULL AUTO_INCREMENT,
  `idventa` int NOT NULL,
  `idproductos` int NOT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `precio_unitario` decimal(10,2) NOT NULL,
  `descuento` decimal(10,2) DEFAULT '0.00',
  `subtotal` decimal(10,2) NOT NULL,
  `cortesia` tinyint(1) DEFAULT '0',
  `beneficio_aplicado` int DEFAULT NULL,
  PRIMARY KEY (`iddetalle`),
  KEY `idventa` (`idventa`),
  KEY `idproductos` (`idproductos`),
  KEY `beneficio_aplicado` (`beneficio_aplicado`),
  CONSTRAINT `ventas_detalle_ibfk_1` FOREIGN KEY (`idventa`) REFERENCES `ventas` (`idventa`),
  CONSTRAINT `ventas_detalle_ibfk_2` FOREIGN KEY (`idproductos`) REFERENCES `productos` (`idproductos`),
  CONSTRAINT `ventas_detalle_ibfk_3` FOREIGN KEY (`beneficio_aplicado`) REFERENCES `puntos_beneficios` (`idbeneficio`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas_detalle`
--

LOCK TABLES `ventas_detalle` WRITE;
/*!40000 ALTER TABLE `ventas_detalle` DISABLE KEYS */;
INSERT INTO `ventas_detalle` VALUES (1,3,5,1,7000.00,0.00,7000.00,0,NULL),(2,3,8,1,7000.00,0.00,7000.00,0,NULL),(3,4,2,1,5000.00,0.00,5000.00,0,NULL),(4,4,16,1,20000.00,0.00,20000.00,0,NULL),(5,5,5,1,7000.00,0.00,7000.00,0,NULL),(6,5,7,1,7000.00,0.00,7000.00,0,NULL),(7,5,8,1,7000.00,0.00,0.00,1,NULL),(8,6,7,1,7000.00,0.00,0.00,1,NULL),(9,6,8,1,7000.00,0.00,7000.00,0,NULL),(10,7,7,1,7000.00,0.00,7000.00,0,NULL),(11,7,16,1,20000.00,0.00,20000.00,0,NULL),(12,7,5,1,7000.00,0.00,7000.00,0,NULL),(13,8,16,1,20000.00,0.00,20000.00,0,NULL),(14,8,6,1,8000.00,0.00,8000.00,0,NULL),(15,9,3,1,37000.00,0.00,37000.00,0,NULL),(16,9,6,1,8000.00,0.00,8000.00,0,NULL),(17,10,9,2,5000.00,0.00,10000.00,0,NULL),(18,11,6,1,8000.00,0.00,8000.00,0,NULL),(19,11,4,1,8000.00,0.00,8000.00,0,NULL),(20,12,10,1,7000.00,0.00,7000.00,0,NULL),(21,13,6,1,8000.00,0.00,8000.00,0,NULL),(22,14,4,1,8000.00,0.00,8000.00,0,NULL),(23,15,6,1,8000.00,0.00,8000.00,0,NULL),(24,16,6,1,8000.00,0.00,8000.00,0,NULL),(25,16,14,1,6000.00,0.00,6000.00,0,NULL),(26,17,10,1,7000.00,0.00,7000.00,0,NULL),(27,17,14,1,6000.00,0.00,6000.00,0,NULL),(28,18,10,1,7000.00,0.00,7000.00,0,NULL),(29,18,14,1,6000.00,0.00,6000.00,0,NULL),(30,19,14,1,6000.00,0.00,6000.00,0,NULL),(31,19,8,1,7000.00,0.00,7000.00,0,NULL),(32,20,8,1,7000.00,0.00,7000.00,0,NULL),(33,20,14,1,6000.00,0.00,6000.00,0,NULL),(34,20,2,1,5000.00,0.00,5000.00,0,NULL),(35,21,9,1,5000.00,0.00,5000.00,0,NULL),(36,21,14,1,6000.00,0.00,6000.00,0,NULL),(37,22,6,1,8000.00,0.00,8000.00,0,NULL),(38,22,14,1,6000.00,0.00,6000.00,0,NULL),(39,23,4,1,8000.00,0.00,8000.00,0,NULL),(40,23,6,1,8000.00,0.00,8000.00,0,NULL),(41,24,3,1,37000.00,0.00,37000.00,0,NULL),(42,25,17,1,8000.00,0.00,8000.00,0,NULL),(43,25,9,1,5000.00,0.00,5000.00,0,NULL),(44,26,9,1,5000.00,0.00,5000.00,0,NULL),(45,26,8,1,7000.00,0.00,7000.00,0,NULL),(46,27,2,1,5000.00,0.00,5000.00,0,NULL),(47,27,14,1,6000.00,0.00,6000.00,0,NULL),(48,28,9,1,5000.00,0.00,5000.00,0,NULL),(49,28,8,1,7000.00,0.00,7000.00,0,NULL),(50,29,2,1,5000.00,0.00,5000.00,0,NULL),(51,29,1,1,10000.00,0.00,10000.00,0,NULL),(52,30,8,1,7000.00,0.00,7000.00,0,NULL),(53,31,8,1,7000.00,0.00,7000.00,0,NULL),(54,31,17,1,8000.00,0.00,8000.00,0,NULL),(55,32,6,1,8000.00,0.00,8000.00,0,NULL),(56,33,7,1,7000.00,0.00,7000.00,0,NULL),(57,34,4,1,8000.00,0.00,8000.00,0,NULL),(58,34,6,1,8000.00,0.00,8000.00,0,NULL),(59,35,17,1,8000.00,0.00,8000.00,0,NULL),(60,35,9,1,5000.00,0.00,5000.00,0,NULL),(61,36,14,1,6000.00,0.00,6000.00,0,NULL),(62,36,17,1,8000.00,0.00,8000.00,0,NULL),(63,37,3,1,37000.00,0.00,37000.00,0,NULL),(64,38,15,1,8000.00,0.00,8000.00,0,NULL),(65,38,7,1,7000.00,0.00,7000.00,0,NULL),(66,38,17,1,8000.00,0.00,8000.00,0,NULL),(67,39,17,1,8000.00,0.00,8000.00,0,NULL),(68,40,17,1,8000.00,0.00,8000.00,0,NULL),(69,41,17,1,8000.00,0.00,8000.00,0,NULL),(70,42,17,1,8000.00,0.00,8000.00,0,NULL),(71,42,9,1,5000.00,0.00,5000.00,0,NULL),(72,42,15,1,8000.00,0.00,8000.00,0,NULL),(73,42,14,1,6000.00,0.00,6000.00,0,NULL);
/*!40000 ALTER TABLE `ventas_detalle` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-14 21:58:07
