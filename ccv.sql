CREATE DATABASE  IF NOT EXISTS `ccv1`;
USE `ccv1`;

DROP TABLE IF EXISTS `address_types`;

INSERT INTO `address_types` VALUES ('Appeals',NULL,'2025-11-21'),('Claims',NULL,'2025-11-21'),('Corporate',NULL,'2025-11-21'),('Remittance',NULL,'2025-11-21');

DROP TABLE IF EXISTS `addresses`;
CREATE TABLE `addresses` (
  `address_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int NOT NULL,
  `address_type` varchar(255) DEFAULT NULL,
  `address_line1` varchar(255) DEFAULT NULL,
  `address_line2` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `zip_code` varchar(20) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`address_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `addresses_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `addresses` VALUES (3,1,'Claims','PO Box 660044',NULL,'Dallas','TX',NULL,'75266',NULL,'2025-11-21');

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
-- Table structure for table `carrier_edits`
--

DROP TABLE IF EXISTS `carrier_edits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carrier_edits` (
  `edit_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int DEFAULT NULL,
  `submitter_name` varchar(255) DEFAULT NULL,
  `submitter_email` varchar(255) DEFAULT NULL,
  `field_name` varchar(50) DEFAULT NULL,
  `old_value` text,
  `new_value` text,
  `status` varchar(20) DEFAULT 'pending',
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`edit_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `carrier_edits_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carrier_edits`
--

INSERT INTO `carrier_edits` VALUES (1,1,'Oluwatosin Ajayi','tosinajy@gmail.com','FULL_RECORD','{\"carrier_id\": 1, \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"state_domicile\": \"TX\", \"am_best_rating\": \"A+\", \"update_dt\": \"2025-11-21\", \"other_carrier_names\": null, \"company_type\": \"Property & Casualty\", \"sbs_company_number\": null, \"sbs_legacy_number\": null, \"cocode\": \"12345\", \"company_licensed_in\": null, \"company_name\": \"BCBS Texas\", \"full_company_name\": null, \"short_name\": null, \"business_type_code\": null, \"insurance_types\": null, \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"transaction\": \"Standard, Real-time\", \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"other_payer_names\": null, \"phones\": [{\"phone_id\": 1, \"carrier_id\": 1, \"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"emails\": [{\"email_id\": 1, \"carrier_id\": 1, \"email_type\": \"Provider Relations\", \"email_address\": \"provider@bcbstx.com\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"websites\": [{\"website_id\": 1, \"carrier_id\": 1, \"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"addresses\": [{\"address_id\": 1, \"carrier_id\": 1, \"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"address_line2\": null, \"city\": \"Dallas\", \"state\": \"TX\", \"country\": \"USA\", \"zip_code\": \"75266\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"line_of_business\": []}','{\"submitter_name\": \"Oluwatosin Ajayi\", \"submitter_email\": \"tosinajy@gmail.com\", \"legal_name\": \"Blue Cross Blue Shield of Texas 1\", \"am_best_rating\": \"A+\", \"state_domicile\": \"TX\", \"cocode\": \"12345\", \"company_name\": \"BCBS Texas\", \"short_name\": \"None\", \"company_licensed_in\": \"None\", \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"transaction\": \"Standard, Real-time\", \"other_payer_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"other_carrier_names\": \"None\", \"phones\": [{\"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\"}], \"emails\": [{\"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\"}], \"websites\": [{\"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\"}], \"addresses\": [{\"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"city\": \"Dallas\", \"state\": \"TX\", \"zip_code\": \"75266\"}], \"lobs\": []}','approved','2025-11-21 18:14:55',1,'2025-11-21 18:16:03'),(2,1,'Oluwatosin Ajayi','aj@panachora.net','FULL_RECORD','{\"carrier_id\": 1, \"legal_name\": \"Blue Cross Blue Shield of Texas 1\", \"state_domicile\": \"TX\", \"am_best_rating\": \"A+\", \"update_dt\": \"2025-11-21\", \"other_carrier_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"cocode\": \"12345\", \"company_licensed_in\": \"None\", \"company_name\": \"BCBS Texas\", \"full_company_name\": null, \"short_name\": \"None\", \"business_type_code\": null, \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"transaction\": \"Standard, Real-time\", \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"other_payer_names\": \"None\", \"phones\": [{\"phone_id\": 2, \"carrier_id\": 1, \"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"emails\": [{\"email_id\": 2, \"carrier_id\": 1, \"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"websites\": [{\"website_id\": 2, \"carrier_id\": 1, \"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"addresses\": [{\"address_id\": 2, \"carrier_id\": 1, \"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"address_line2\": null, \"city\": \"Dallas\", \"state\": \"TX\", \"country\": null, \"zip_code\": \"75266\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"line_of_business\": []}','{\"submitter_name\": \"Oluwatosin Ajayi\", \"submitter_email\": \"aj@panachora.net\", \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"am_best_rating\": \"A+\", \"state_domicile\": \"TX\", \"cocode\": \"12345\", \"company_name\": \"BCBS Texas\", \"short_name\": \"None\", \"company_licensed_in\": \"None\", \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"transaction\": \"Standard, Real-time\", \"other_payer_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"other_carrier_names\": \"None\", \"phones\": [{\"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\"}], \"emails\": [{\"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\"}], \"websites\": [{\"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\"}], \"addresses\": [{\"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"city\": \"Dallas\", \"state\": \"TX\", \"zip_code\": \"75266\"}], \"lobs\": []}','approved','2025-11-21 18:16:38',1,'2025-11-21 18:33:35'),(3,1,'Oluwatosin Ajayi','tosinajy@gmail.com','FULL_RECORD','{\"carrier_id\": 1, \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"state_domicile\": \"TX\", \"am_best_rating\": \"A+\", \"update_dt\": \"2025-11-21\", \"other_carrier_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"cocode\": \"12345\", \"company_licensed_in\": \"None\", \"company_name\": \"BCBS Texas\", \"full_company_name\": null, \"short_name\": \"None\", \"business_type_code\": null, \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"transaction\": \"Standard, Real-time\", \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"other_payer_names\": \"None\", \"phones\": [{\"phone_id\": 3, \"carrier_id\": 1, \"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"emails\": [{\"email_id\": 3, \"carrier_id\": 1, \"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"websites\": [{\"website_id\": 3, \"carrier_id\": 1, \"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"addresses\": [{\"address_id\": 3, \"carrier_id\": 1, \"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"address_line2\": null, \"city\": \"Dallas\", \"state\": \"TX\", \"country\": null, \"zip_code\": \"75266\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"line_of_business\": []}','{\"submitter_name\": \"Oluwatosin Ajayi\", \"submitter_email\": \"tosinajy@gmail.com\", \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"am_best_rating\": \"A+\", \"state_domicile\": \"TX\", \"cocode\": \"12345\", \"company_name\": \"BCBS Texas\", \"short_name\": \"None\", \"company_licensed_in\": \"None\", \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"transaction\": \"Standard, Real-time\", \"other_payer_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"other_carrier_names\": \"None\", \"phones\": [{\"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\"}], \"emails\": [{\"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\"}], \"websites\": [{\"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\"}], \"addresses\": [{\"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"city\": \"Dallas\", \"state\": \"TX\", \"zip_code\": \"75266\"}], \"lobs\": []}','pending','2025-11-21 18:33:59',NULL,NULL),(4,1,'Oluwatosin Ajayi','tosinajy@gmail.com','FULL_RECORD','{\"carrier_id\": 1, \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"state_domicile\": \"TX\", \"am_best_rating\": \"A+\", \"update_dt\": \"2025-11-21\", \"other_carrier_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"cocode\": \"12345\", \"company_licensed_in\": \"None\", \"company_name\": \"BCBS Texas\", \"full_company_name\": null, \"short_name\": \"None\", \"business_type_code\": null, \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"transaction\": \"Standard, Real-time\", \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"other_payer_names\": \"None\", \"phones\": [{\"phone_id\": 3, \"carrier_id\": 1, \"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"emails\": [{\"email_id\": 3, \"carrier_id\": 1, \"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"websites\": [{\"website_id\": 3, \"carrier_id\": 1, \"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"addresses\": [{\"address_id\": 3, \"carrier_id\": 1, \"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"address_line2\": null, \"city\": \"Dallas\", \"state\": \"TX\", \"country\": null, \"zip_code\": \"75266\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"line_of_business\": []}','{\"submitter_name\": \"Oluwatosin Ajayi\", \"submitter_email\": \"tosinajy@gmail.com\", \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"am_best_rating\": \"A+\", \"state_domicile\": \"TX\", \"cocode\": \"12345\", \"company_name\": \"BCBS Texas\", \"short_name\": \"None\", \"company_licensed_in\": \"None\", \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"transaction\": \"Standard, Real-time\", \"other_payer_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"other_carrier_names\": \"None\", \"phones\": [{\"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\"}], \"emails\": [{\"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\"}], \"websites\": [{\"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\"}], \"addresses\": [{\"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"city\": \"Dallas\", \"state\": \"TX\", \"zip_code\": \"75266\"}], \"lobs\": []}','pending','2025-11-21 18:35:21',NULL,NULL),(5,1,'Oluwatosin Ajayi','tosinajy@gmail.com','FULL_RECORD','{\"carrier_id\": 1, \"legal_name\": \"Blue Cross Blue Shield of Texas\", \"state_domicile\": \"TX\", \"am_best_rating\": \"A+\", \"update_dt\": \"2025-11-21\", \"other_carrier_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"cocode\": \"12345\", \"company_licensed_in\": \"None\", \"company_name\": \"BCBS Texas\", \"full_company_name\": null, \"short_name\": \"None\", \"business_type_code\": null, \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"transaction\": \"Standard, Real-time\", \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"other_payer_names\": \"None\", \"phones\": [{\"phone_id\": 3, \"carrier_id\": 1, \"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"emails\": [{\"email_id\": 3, \"carrier_id\": 1, \"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"websites\": [{\"website_id\": 3, \"carrier_id\": 1, \"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"addresses\": [{\"address_id\": 3, \"carrier_id\": 1, \"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"address_line2\": null, \"city\": \"Dallas\", \"state\": \"TX\", \"country\": null, \"zip_code\": \"75266\", \"update_by\": null, \"update_dt\": \"2025-11-21\"}], \"line_of_business\": []}','{\"submitter_name\": \"Oluwatosin Ajayi\", \"submitter_email\": \"tosinajy@gmail.com\", \"legal_name\": \"Blue Cross Blue Shield of Texas 1\", \"am_best_rating\": \"A+\", \"state_domicile\": \"TX\", \"cocode\": \"12345\", \"company_name\": \"BCBS Texas\", \"short_name\": \"None\", \"company_licensed_in\": \"None\", \"insurance_types\": \"None\", \"payer_code\": \"BCBS01\", \"enrollment\": 1, \"attachment\": 1, \"wc_auto\": 0, \"available\": 1, \"non_par\": 0, \"transaction\": \"Standard, Real-time\", \"other_payer_names\": \"None\", \"company_type\": \"Property & Casualty\", \"sbs_company_number\": \"None\", \"sbs_legacy_number\": \"None\", \"other_carrier_names\": \"None\", \"phones\": [{\"phone_type\": \"Claims\", \"phone_number\": \"800-555-0199\"}], \"emails\": [{\"email_type\": \"\", \"email_address\": \"provider@bcbstx.com\"}], \"websites\": [{\"website_type\": \"Provider Portal\", \"website_url\": \"https://availity.com/bcbstx\"}], \"addresses\": [{\"address_type\": \"Claims\", \"address_line1\": \"PO Box 660044\", \"city\": \"Dallas\", \"state\": \"TX\", \"zip_code\": \"75266\"}], \"lobs\": []}','pending','2025-11-21 19:06:26',NULL,NULL);

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
-- Table structure for table `clearing_houses`
--

DROP TABLE IF EXISTS `clearing_houses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clearing_houses` (
  `clearing_house_id` int NOT NULL AUTO_INCREMENT,
  `payer_id` int NOT NULL,
  `clearing_house` varchar(255) DEFAULT NULL,
  `clearing_house_url` varchar(255) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`clearing_house_id`),
  KEY `payer_id` (`payer_id`),
  CONSTRAINT `clearing_houses_ibfk_1` FOREIGN KEY (`payer_id`) REFERENCES `payers` (`payer_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clearing_houses`
--

INSERT INTO `clearing_houses` VALUES (1,1,'Availity','https://availity.com',NULL,'2025-11-21');

--
-- Table structure for table `company_types`
--

DROP TABLE IF EXISTS `company_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_types` (
  `company_type` varchar(255) NOT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`company_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_types`
--

INSERT INTO `company_types` VALUES ('HMO',NULL,'2025-11-21'),('Life & Health',NULL,'2025-11-21'),('PPO',NULL,'2025-11-21'),('Property & Casualty',NULL,'2025-11-21');

--
-- Table structure for table `email_types`
--

DROP TABLE IF EXISTS `email_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_types` (
  `email_type` varchar(255) NOT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`email_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_types`
--

INSERT INTO `email_types` VALUES ('Appeals',NULL,'2025-11-21'),('Claims',NULL,'2025-11-21'),('Contracting',NULL,'2025-11-21'),('Support',NULL,'2025-11-21');

--
-- Table structure for table `emails`
--

DROP TABLE IF EXISTS `emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emails` (
  `email_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int NOT NULL,
  `email_type` varchar(255) DEFAULT NULL,
  `email_address` varchar(255) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`email_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `emails_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emails`
--

INSERT INTO `emails` VALUES (3,1,'','provider@bcbstx.com',NULL,'2025-11-21');

--
-- Table structure for table `line_of_business`
--

DROP TABLE IF EXISTS `line_of_business`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `line_of_business` (
  `lob_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int NOT NULL,
  `lob` varchar(255) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`lob_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `line_of_business_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `line_of_business`
--


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
  `carrier_id` int DEFAULT NULL,
  `payer_code` varchar(50) DEFAULT NULL,
  `other_payer_names` text,
  `enrollment` bit(1) DEFAULT b'0',
  `attachment` bit(1) DEFAULT b'0',
  `transaction` varchar(1000) DEFAULT NULL,
  `wc_auto` bit(1) DEFAULT b'0',
  `available` bit(1) DEFAULT b'1',
  `non_par` bit(1) DEFAULT b'0',
  PRIMARY KEY (`payer_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `payers_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payers`
--

INSERT INTO `payers` VALUES (1,1,'BCBS01','None',_binary '',_binary '','Standard, Real-time',_binary '\0',_binary '',_binary '\0');

--
-- Table structure for table `phone_types`
--

DROP TABLE IF EXISTS `phone_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phone_types` (
  `phone_type` varchar(255) NOT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`phone_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phone_types`
--

INSERT INTO `phone_types` VALUES ('Claims',NULL,'2025-11-21'),('Eligibility',NULL,'2025-11-21'),('Prior Auth',NULL,'2025-11-21'),('Provider Relations',NULL,'2025-11-21');

--
-- Table structure for table `phones`
--

DROP TABLE IF EXISTS `phones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phones` (
  `phone_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int NOT NULL,
  `phone_type` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`phone_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `phones_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phones`
--

INSERT INTO `phones` VALUES (3,1,'Claims','800-555-0199',NULL,'2025-11-21');

--
-- Table structure for table `us_states`
--

DROP TABLE IF EXISTS `us_states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_states` (
  `state_id` varchar(255) NOT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`state_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `us_states`
--

INSERT INTO `us_states` VALUES ('CA',NULL,'2025-11-21'),('FL',NULL,'2025-11-21'),('IL',NULL,'2025-11-21'),('NY',NULL,'2025-11-21'),('OH',NULL,'2025-11-21'),('TX',NULL,'2025-11-21');

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

--
-- Table structure for table `website_types`
--

DROP TABLE IF EXISTS `website_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_types` (
  `website_type` varchar(255) NOT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`website_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_types`
--

INSERT INTO `website_types` VALUES ('Claims Upload',NULL,'2025-11-21'),('Main Site',NULL,'2025-11-21'),('Provider Portal',NULL,'2025-11-21');

--
-- Table structure for table `websites`
--

DROP TABLE IF EXISTS `websites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `websites` (
  `website_id` int NOT NULL AUTO_INCREMENT,
  `carrier_id` int NOT NULL,
  `website_type` varchar(255) DEFAULT NULL,
  `website_url` varchar(255) DEFAULT NULL,
  `update_by` varchar(255) DEFAULT NULL,
  `update_dt` date DEFAULT NULL,
  PRIMARY KEY (`website_id`),
  KEY `carrier_id` (`carrier_id`),
  CONSTRAINT `websites_ibfk_1` FOREIGN KEY (`carrier_id`) REFERENCES `carriers` (`carrier_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `websites`
--

INSERT INTO `websites` VALUES (3,1,'Provider Portal','https://availity.com/bcbstx',NULL,'2025-11-21');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
