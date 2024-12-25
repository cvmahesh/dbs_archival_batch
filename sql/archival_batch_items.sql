-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               11.6.2-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for batch_db
DROP DATABASE IF EXISTS `batch_db`;
CREATE DATABASE IF NOT EXISTS `batch_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `batch_db`;

-- Dumping structure for table batch_db.archival_batch_items
DROP TABLE IF EXISTS `archival_batch_items`;
CREATE TABLE IF NOT EXISTS `archival_batch_items` (
  `ID` int(11) NOT NULL,
  `batch_name` varchar(50) NOT NULL,
  `data_folder` varchar(50) NOT NULL,
  `archive_folder` varchar(50) NOT NULL,
  `delete_folder` varchar(50) NOT NULL,
  `archive_days` int(11) NOT NULL DEFAULT 0,
  `delete_days` int(11) NOT NULL DEFAULT 0,
  `is_active` varchar(50) NOT NULL,
  `email_receipt` varchar(500) DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `created_on` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Dumping data for table batch_db.archival_batch_items: ~2 rows (approximately)
INSERT INTO `archival_batch_items` (`ID`, `batch_name`, `data_folder`, `archive_folder`, `delete_folder`, `archive_days`, `delete_days`, `is_active`, `email_receipt`, `created_by`, `created_on`) VALUES
	(1, 'batch1', 'C:\\workspace\\testing\\data\\folder1', 'C:\\workspace\\testing\\archive\\folder1', 'C:\\workspace\\testing\\delete\\folder1', 1, 1, 'true', 'rush2cvmahesh@gmail.com', 'system', '24/12/2024'),
	(2, 'batch1', 'C:\\workspace\\testing\\data\\folder2', 'C:\\workspace\\testing\\archive\\folder2', 'C:\\workspace\\testingdelete\\folder2', 1, 1, 'true', 'rush2cvmahesh@gmail.com', 'system', '24/12/2024');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
