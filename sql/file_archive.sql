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

-- Dumping structure for table batch_db.file_archive
DROP TABLE IF EXISTS `file_archive`;
CREATE TABLE IF NOT EXISTS `file_archive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(100) DEFAULT NULL,
  `source_path` varchar(100) DEFAULT NULL,
  `archive_path` varchar(100) DEFAULT NULL,
  `archived_at` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table batch_db.file_archive: ~0 rows (approximately)
INSERT INTO `file_archive` (`id`, `file_name`, `source_path`, `archive_path`, `archived_at`) VALUES
	(1, 'file1.eml', 'C:\\workspace\\testing\\data\\folder1', 'C:\\workspace\\testing\\archive\\folder1', '2024-12-25'),
	(2, 'file1.eml', 'C:\\workspace\\testing\\archive\\folder1', 'C:\\workspace\\testing\\delete\\folder1', '2024-12-25'),
	(3, 'file2.eml', 'C:\\workspace\\testing\\data\\folder2', 'C:\\workspace\\testing\\archive\\folder2', '2024-12-25');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
