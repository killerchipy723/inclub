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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jornadas_productos`
--

LOCK TABLES `jornadas_productos` WRITE;
/*!40000 ALTER TABLE `jornadas_productos` DISABLE KEYS */;
INSERT INTO `jornadas_productos` VALUES (1,11,2),(2,11,5),(3,11,6),(4,11,7),(5,11,8),(6,11,10),(7,11,16),(8,12,1),(18,12,2),(19,12,3),(9,12,4),(10,12,6),(20,12,7),(11,12,8),(12,12,9),(13,12,10),(14,12,13),(15,12,14),(16,12,15),(17,12,17);
/*!40000 ALTER TABLE `jornadas_productos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-14 21:40:38
