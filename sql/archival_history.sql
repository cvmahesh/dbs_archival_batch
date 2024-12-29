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

-- Dumping structure for table batch_db.archival_history
DROP TABLE IF EXISTS `archival_history`;
CREATE TABLE IF NOT EXISTS `archival_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` uuid NOT NULL,
  `batch_name` varchar(50) DEFAULT NULL,
  `file_name` varchar(100) NOT NULL,
  `source_path` varchar(100) NOT NULL,
  `archive_path` varchar(100) NOT NULL,
  `archived_at` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table batch_db.archival_history: ~4 rows (approximately)
INSERT INTO `archival_history` (`id`, `uuid`, `batch_name`, `file_name`, `source_path`, `archive_path`, `archived_at`) VALUES
	(45, '00000000-0000-0000-0000-000000000000', NULL, 'file1.eml', 'C:\\workspace\\testing\\data\\folder1', 'C:\\workspace\\testing\\RollingFolders\\20241229\\archive\\folder1\\file1.eml.zip', '2024-12-29'),
	(46, '00000000-0000-0000-0000-000000000000', NULL, 'file1_1.eml', 'C:\\workspace\\testing\\data\\folder1', 'C:\\workspace\\testing\\RollingFolders\\20241229\\archive\\folder1\\file1_1.eml.zip', '2024-12-29'),
	(47, '00000000-0000-0000-0000-000000000000', NULL, 'file2-1.eml', 'C:\\workspace\\testing\\data\\folder2', 'C:\\workspace\\testing\\RollingFolders\\20241229\\archive\\folder2\\file2-1.eml.zip', '2024-12-29'),
	(48, '00000000-0000-0000-0000-000000000000', NULL, 'file2.eml', 'C:\\workspace\\testing\\data\\folder2', 'C:\\workspace\\testing\\RollingFolders\\20241229\\archive\\folder2\\file2.eml.zip', '2024-12-29');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;