CREATE DATABASE  IF NOT EXISTS `carrier_code_verify` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `carrier_code_verify`;
-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: carrier_code_verify
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int DEFAULT NULL,
  `action_type` varchar(50) DEFAULT NULL,
  `description` text,
  `changed_by` varchar(100) DEFAULT NULL,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_log`
--

INSERT INTO `audit_log` VALUES (1,1,'full_update','Full Record Update via Admin Panel','Submitter: Oluwatosin Ajayi','2025-11-21 18:16:03'),(2,1,'full_update','Full Record Update via Admin Panel','Submitter: Oluwatosin Ajayi','2025-11-21 18:33:35');

--
-- Table structure for table `carriers`
--

DROP TABLE IF EXISTS `carriers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carriers` (
  `carrier_id` int NOT NULL AUTO_INCREMENT,
  `legal_name` varchar(1000) NOT NULL,
  `payer_id` int DEFAULT NULL,
  `naic_id` int DEFAULT NULL,
  `other_carrier_names` varchar(1000) DEFAULT NULL,
  `state_domicile` varchar(2) DEFAULT NULL,
  `company_type` varchar(255) DEFAULT NULL,
  `sbs_company_number` varchar(20) DEFAULT NULL,
  `sbs_legacy_number` varchar(20) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  `am_best_rating` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`carrier_id`),
  KEY `fk_carriers_payer` (`payer_id`),
  KEY `fk_carriers_naic` (`naic_id`),
  CONSTRAINT `fk_carriers_naic` FOREIGN KEY (`naic_id`) REFERENCES `naic` (`naic_id`),
  CONSTRAINT `fk_carriers_payer` FOREIGN KEY (`payer_id`) REFERENCES `payers` (`payer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carriers`
--

INSERT INTO `carriers` VALUES (1,'Blue Cross Blue Shield of Texas',1,1,'None','TX','Property & Casualty','None','None',NULL,'2025-11-21','A+');

--
-- Table structure for table `naic`
--

DROP TABLE IF EXISTS `naic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `naic` (
  `naic_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int DEFAULT NULL,
  `company_name` varchar(1000) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `insurance_types` varchar(255) DEFAULT NULL,
  `company_licensed_in` varchar(255) DEFAULT NULL,
  `cocode` varchar(20) DEFAULT NULL,
  `full_company_name` varchar(1000) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `address_line_1` varchar(255) DEFAULT NULL,
  `address_line_2` varchar(255) DEFAULT NULL,
  `business_type_code` varchar(2) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `full_name` varchar(1000) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `short_name` varchar(255) DEFAULT NULL,
  `state` varchar(2) DEFAULT NULL,
  `zip` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`naic_id`),
  UNIQUE KEY `cocode` (`cocode`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `naic_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `naic`
--

INSERT INTO `naic` VALUES (1,1,'BCBS Texas',NULL,'None','None','12345',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'None','TX',NULL);

--
-- Table structure for table `payers`
--

DROP TABLE IF EXISTS `payers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payers` (
  `payer_id` int NOT NULL AUTO_INCREMENT,
  `payer_code` varchar(50) DEFAULT NULL,
  `enrollment` bit(1) DEFAULT b'0',
  `attachment` bit(1) DEFAULT b'0',
  `transaction` varchar(1000) DEFAULT NULL,
  `wc_auto` bit(1) DEFAULT b'0',
  `available` bit(1) DEFAULT b'1',
  `non_par` bit(1) DEFAULT b'0',
  `clearing_house` varchar(255) DEFAULT NULL,
  `payer_name` varchar(255) DEFAULT NULL,
  `comment` text,
  `verify_url` varchar(255) DEFAULT NULL,
  `naic_id` int DEFAULT NULL,
  `mapping_status` varchar(50) DEFAULT 'unassigned',
  PRIMARY KEY (`payer_id`),
  KEY `fk_payers_naic` (`naic_id`),
  CONSTRAINT `fk_payers_naic` FOREIGN KEY (`naic_id`) REFERENCES `naic` (`naic_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payers`
--

INSERT INTO `payers` VALUES (1,'BCBS01',_binary '',_binary '','Standard, Real-time',_binary '\0',_binary '',_binary '\0',NULL,NULL,NULL,NULL,NULL,'unassigned');

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'admin',
  `email` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

INSERT INTO `users` VALUES (1,'admin','scrypt:32768:8:1$MzgXhF0gLHwNmLk9$bd48d7ca43190112fe4cdfa519001ba0225cc16edcb13aeabc2808b63177186ed323d149456a23a08958989eedc26339df0ade6565f5228906eac92e270889cd','admin','admin@example.com','2025-11-21 05:42:35');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
