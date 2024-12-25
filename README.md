# Batch Process Archival Script

## Prerequisite

### PIP

Refer the link below to install pip 
https://packaging.python.org/en/latest/tutorials/installing-packages/

 


## How to execute
'''
py -m pip install -r requirements.txt

'''


Maria DB
CREATE DATABASE `batch_db` /*!40100 COLLATE 'utf8mb4_uca1400_ai_ci' */;

CREATE TABLE `archival_batch_items` (
	`ID` INT NULL,
	`batch_name` VARCHAR(50) NULL DEFAULT NULL,
	`data_folder` VARCHAR(50) NULL DEFAULT NULL,
	`archive_folder` VARCHAR(50) NULL DEFAULT NULL,
	`delete_folder` VARCHAR(50) NULL DEFAULT NULL,
	`archive_days` VARCHAR(50) NULL DEFAULT NULL,
	`delete_days` VARCHAR(50) NULL DEFAULT NULL,
	`is_active` VARCHAR(50) NULL DEFAULT NULL,
	`email_receipt` VARCHAR(500) NULL DEFAULT NULL,
	`created_by` VARCHAR(50) NULL DEFAULT NULL,
	`created_on` VARCHAR(50) NULL DEFAULT NULL
)
COLLATE='utf8mb4_uca1400_ai_ci'
;
ALTER DATABASE batch_db CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;



## Commnd to run the program 
'''
python3 .\move_files.py --archive 
''' 