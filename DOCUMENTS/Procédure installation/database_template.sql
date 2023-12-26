-- MySQL dump 10.13  Distrib 8.0.35, for Linux (x86_64)
--
-- Host: localhost    Database: SAE302
-- ------------------------------------------------------
-- Server version	8.0.35-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `MESSAGES_P2P`
--

DROP TABLE IF EXISTS `MESSAGES_P2P`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MESSAGES_P2P` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_from` int NOT NULL,
  `message_to` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message_content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MESSAGES_P2P`
--

LOCK TABLES `MESSAGES_P2P` WRITE;
/*!40000 ALTER TABLE `MESSAGES_P2P` DISABLE KEYS */;
/*!40000 ALTER TABLE `MESSAGES_P2P` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MESSAGES_blabla`
--

DROP TABLE IF EXISTS `MESSAGES_blabla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MESSAGES_blabla` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_user` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message_content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MESSAGES_blabla`
--

LOCK TABLES `MESSAGES_blabla` WRITE;
/*!40000 ALTER TABLE `MESSAGES_blabla` DISABLE KEYS */;
/*!40000 ALTER TABLE `MESSAGES_blabla` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MESSAGES_comptabilite`
--

DROP TABLE IF EXISTS `MESSAGES_comptabilite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MESSAGES_comptabilite` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_user` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message_content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MESSAGES_comptabilite`
--

LOCK TABLES `MESSAGES_comptabilite` WRITE;
/*!40000 ALTER TABLE `MESSAGES_comptabilite` DISABLE KEYS */;
/*!40000 ALTER TABLE `MESSAGES_comptabilite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MESSAGES_general`
--

DROP TABLE IF EXISTS `MESSAGES_general`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MESSAGES_general` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_user` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message_content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MESSAGES_general`
--

LOCK TABLES `MESSAGES_general` WRITE;
/*!40000 ALTER TABLE `MESSAGES_general` DISABLE KEYS */;
/*!40000 ALTER TABLE `MESSAGES_general` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MESSAGES_informatique`
--

DROP TABLE IF EXISTS `MESSAGES_informatique`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MESSAGES_informatique` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_user` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message_content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MESSAGES_informatique`
--

LOCK TABLES `MESSAGES_informatique` WRITE;
/*!40000 ALTER TABLE `MESSAGES_informatique` DISABLE KEYS */;
/*!40000 ALTER TABLE `MESSAGES_informatique` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MESSAGES_marketing`
--

DROP TABLE IF EXISTS `MESSAGES_marketing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MESSAGES_marketing` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_user` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message_content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MESSAGES_marketing`
--

LOCK TABLES `MESSAGES_marketing` WRITE;
/*!40000 ALTER TABLE `MESSAGES_marketing` DISABLE KEYS */;
/*!40000 ALTER TABLE `MESSAGES_marketing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Salons`
--

DROP TABLE IF EXISTS `Salons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Salons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(30) NOT NULL,
  `messages` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Salons`
--

LOCK TABLES `Salons` WRITE;
/*!40000 ALTER TABLE `Salons` DISABLE KEYS */;
INSERT INTO `Salons` VALUES (1,'Général','MESSAGES_general'),(2,'Blabla','MESSAGES_blabla'),(3,'Comptabilité','MESSAGES_comptabilite'),(4,'Informatique','MESSAGES_informatique'),(5,'Marketing','MESSAGES_marketing');
/*!40000 ALTER TABLE `Salons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) NOT NULL,
  `First_name` varchar(50) DEFAULT NULL,
  `Last_name` varchar(50) DEFAULT NULL,
  `Password` varchar(30) NOT NULL,
  `Mail` varchar(50) DEFAULT NULL,
  `user_type` varchar(12) NOT NULL,
  `is_banned` tinyint(1) DEFAULT NULL,
  `is_connected` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (26,'admin','admin','admin','admin','admin@mail.com','ADMIN',0,'UNDEFINED');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banned_users`
--

DROP TABLE IF EXISTS `banned_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banned_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `UID` int NOT NULL,
  `ban_or_kick` varchar(10) DEFAULT NULL,
  `ip_adress` varchar(20) DEFAULT NULL,
  `duration` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banned_users`
--

LOCK TABLES `banned_users` WRITE;
/*!40000 ALTER TABLE `banned_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `banned_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_friends`
--

DROP TABLE IF EXISTS `user_friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_friends` (
  `id` int NOT NULL AUTO_INCREMENT,
  `UID` int NOT NULL,
  `friend_UID` int NOT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_friends`
--

LOCK TABLES `user_friends` WRITE;
/*!40000 ALTER TABLE `user_friends` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_friends` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_rooms`
--

DROP TABLE IF EXISTS `user_rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `UID` int NOT NULL,
  `Salon_id` int NOT NULL,
  `Access` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_rooms`
--

LOCK TABLES `user_rooms` WRITE;
/*!40000 ALTER TABLE `user_rooms` DISABLE KEYS */;
INSERT INTO `user_rooms` VALUES (26,26,1,'YES'),(27,26,2,'YES'),(28,26,3,'YES'),(29,26,4,'YES'),(30,26,5,'YES');
/*!40000 ALTER TABLE `user_rooms` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-19 16:21:49
