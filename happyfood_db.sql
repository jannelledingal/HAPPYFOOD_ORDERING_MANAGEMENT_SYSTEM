-- -----------------------------------------------------
-- Database: happyfood_db
-- Compatible with XAMPP / MySQL 8.x
-- -----------------------------------------------------
CREATE DATABASE IF NOT EXISTS `happyfood_db`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `happyfood_db`;

-- -----------------------------------------------------
-- Table: menus
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `menus` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category` VARCHAR(64) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table: orders
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `items` JSON NOT NULL,
  `total` DECIMAL(10,2) NOT NULL,
  `status` VARCHAR(32) NOT NULL DEFAULT 'pending',
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table: users
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(128) NOT NULL,
  `role` VARCHAR(32) NOT NULL DEFAULT 'admin',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Default admin user
-- (password: admin123 -> SHA256 hash)
-- -----------------------------------------------------
INSERT INTO `users` (`username`, `password_hash`, `role`)
VALUES
('admin', SHA2('admin123', 256), 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- -----------------------------------------------------
-- Sample menu data
-- -----------------------------------------------------
INSERT INTO `menus` (`category`, `name`, `price`) VALUES
('Meals', 'Cheeseburger', 99.00),
('Meals', 'Fried Chicken', 120.00),
('Drinks', 'Coke', 25.00),
('Drinks', 'Iced Tea', 30.00),
('Desserts', 'Ice Cream', 50.00),
('Desserts', 'Brownie', 45.00)
ON DUPLICATE KEY UPDATE name=name;

