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
-- Table structure for table `detalle_entradas`
--

DROP TABLE IF EXISTS `detalle_entradas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_entradas` (
  `iddetalle` int NOT NULL AUTO_INCREMENT,
  `idventa` int NOT NULL,
  `idsector` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`iddetalle`),
  KEY `idventa` (`idventa`),
  KEY `idsector` (`idsector`),
  CONSTRAINT `detalle_entradas_ibfk_1` FOREIGN KEY (`idventa`) REFERENCES `ventas_entradas` (`idventa`),
  CONSTRAINT `detalle_entradas_ibfk_2` FOREIGN KEY (`idsector`) REFERENCES `sectores` (`idsector`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `precios_entradas`
--

DROP TABLE IF EXISTS `precios_entradas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `precios_entradas` (
  `idprecio` int NOT NULL AUTO_INCREMENT,
  `idjornada` int NOT NULL,
  `idsector` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_general_ci DEFAULT 'Activo',
  PRIMARY KEY (`idprecio`),
  KEY `idjornada` (`idjornada`),
  KEY `idsector` (`idsector`),
  CONSTRAINT `precios_entradas_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornadas` (`idjornada`),
  CONSTRAINT `precios_entradas_ibfk_2` FOREIGN KEY (`idsector`) REFERENCES `sectores` (`idsector`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sectores`
--

DROP TABLE IF EXISTS `sectores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sectores` (
  `idsector` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_general_ci DEFAULT 'Activo',
  PRIMARY KEY (`idsector`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sectores_entradas`
--

DROP TABLE IF EXISTS `sectores_entradas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sectores_entradas` (
  `idsector` int NOT NULL AUTO_INCREMENT,
  `idjornada` int NOT NULL,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `estado` enum('Activo','Inactivo') COLLATE utf8mb4_general_ci DEFAULT 'Activo',
  PRIMARY KEY (`idsector`),
  KEY `idjornada` (`idjornada`),
  CONSTRAINT `sectores_entradas_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornadas` (`idjornada`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ventas_entradas`
--

DROP TABLE IF EXISTS `ventas_entradas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas_entradas` (
  `idventa` int NOT NULL AUTO_INCREMENT,
  `idjornada` int NOT NULL,
  `idusuario` int NOT NULL,
  `cliente` int NOT NULL DEFAULT '1',
  `fecha_emision` datetime DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(10,2) NOT NULL,
  `estado` enum('OK','ANULADA') COLLATE utf8mb4_general_ci DEFAULT 'OK',
  PRIMARY KEY (`idventa`),
  KEY `idjornada` (`idjornada`),
  KEY `idusuario` (`idusuario`),
  KEY `fk_ventas_entradas_cliente` (`cliente`),
  CONSTRAINT `fk_ventas_entradas_cliente` FOREIGN KEY (`cliente`) REFERENCES `clientes` (`idclientes`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ventas_entradas_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornadas` (`idjornada`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ventas_entradas_detalle`
--

DROP TABLE IF EXISTS `ventas_entradas_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas_entradas_detalle` (
  `iddetalle` int NOT NULL AUTO_INCREMENT,
  `idventa` int NOT NULL,
  `idsector` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`iddetalle`),
  KEY `idventa` (`idventa`),
  KEY `idsector` (`idsector`),
  CONSTRAINT `ventas_entradas_detalle_ibfk_1` FOREIGN KEY (`idventa`) REFERENCES `ventas_entradas` (`idventa`),
  CONSTRAINT `ventas_entradas_detalle_ibfk_2` FOREIGN KEY (`idsector`) REFERENCES `sectores_entradas` (`idsector`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-16  7:51:36
