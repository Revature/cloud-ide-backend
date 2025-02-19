-- Drop the database if it already exists (optional).
DROP DATABASE IF EXISTS cloud_id_dev;

-- Create a new database.
CREATE DATABASE cloud_id_dev;

-- Switch to the new database.
USE cloud_id_dev;

-- Create the User table.
-- Adjust column names, types, and constraints to suit your needs.
CREATE TABLE `User` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;