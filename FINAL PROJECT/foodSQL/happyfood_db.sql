-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 07, 2025 at 07:19 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `happyfood_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `menus`
--

CREATE TABLE `menus` (
  `id` int(11) NOT NULL,
  `category` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menus`
--

INSERT INTO `menus` (`id`, `category`, `name`, `price`) VALUES
(1, 'Meals', 'Cheeseburger', 99.00),
(2, 'Meals', 'Fried Chicken', 120.00),
(3, 'Drinks', 'Coke', 25.00),
(4, 'Drinks', 'Iced Tea', 30.00),
(5, 'Desserts', 'Ice Cream', 50.00),
(6, 'Desserts', 'Brownie', 45.00),
(7, 'Meals', 'Fried Chicken Meal', 120.00),
(9, 'Drinks', 'Milk Tea (Okinawa)', 75.00),
(10, 'Desserts', 'Halo-Halo Special', 90.00),
(12, 'Desserts', 'Chocolate Brownie', 45.00),
(13, 'Meals', 'Chicken Teriyaki Bowl', 140.00),
(14, 'Desserts', 'Cheesecake Slice', 50.00),
(15, 'Meals', 'Cheesy Beef Burger', 99.00),
(16, 'Meals', 'Fried Chicken Meal', 120.00),
(17, 'Meals', 'Chicken Fillet Rice Bowl', 110.00),
(18, 'Meals', 'Pork Sisig with Egg', 130.00),
(19, 'Meals', 'Beef Tapa Rice Meal', 135.00),
(20, 'Meals', 'Chicken Teriyaki Bowl', 140.00),
(21, 'Meals', 'Grilled Liempo Rice Meal', 150.00),
(22, 'Meals', 'Spaghetti Bolognese', 95.00),
(23, 'Meals', 'Chicken Alfredo Pasta', 120.00),
(24, 'Meals', 'Adobo Rice Bowl', 115.00),
(25, 'Meals', 'Longsilog (Longganisa + Egg + Rice)', 105.00),
(26, 'Meals', 'Tapsilog (Beef Tapa + Egg + Rice)', 115.00),
(27, 'Meals', 'Chopsuey with Rice', 110.00),
(28, 'Meals', 'Chicken BBQ Meal', 125.00),
(29, 'Drinks', 'Coca-Cola in Can', 25.00),
(30, 'Drinks', 'Sprite in Can', 25.00),
(31, 'Drinks', 'Royal Tru-Orange', 25.00),
(32, 'Drinks', 'Iced Tea (Lemon)', 30.00),
(33, 'Drinks', 'Iced Coffee', 45.00),
(34, 'Drinks', 'Bottled Water', 20.00),
(35, 'Drinks', 'Milk Tea (Classic)', 80.00),
(36, 'Drinks', 'Milk Tea (Okinawa)', 90.00),
(37, 'Drinks', 'Fruit Shake (Mango)', 70.00),
(38, 'Drinks', 'Fruit Shake (Watermelon)', 70.00),
(39, 'Drinks', 'Hot Chocolate', 50.00),
(40, 'Drinks', 'Cappuccino', 65.00),
(41, 'Drinks', 'Café Latte', 70.00),
(42, 'Desserts', 'Ice Cream Sundae', 50.00),
(43, 'Desserts', 'Chocolate Brownie', 45.00),
(44, 'Desserts', 'Mango Float', 70.00),
(45, 'Desserts', 'Leche Flan', 55.00),
(46, 'Desserts', 'Buko Pandan', 60.00),
(47, 'Desserts', 'Choco Lava Cake', 95.00),
(48, 'Desserts', 'Banana Split', 85.00),
(49, 'Desserts', 'Halo-Halo Special', 90.00),
(50, 'Desserts', 'Cheesecake Slice', 100.00),
(51, 'Desserts', 'Cupcake (Chocolate)', 40.00),
(52, 'Desserts', 'Blueberry Muffin', 55.00),
(53, 'Combos', 'Burger Combo Meal', 145.00),
(54, 'Combos', 'Chicken Rice Combo', 160.00),
(55, 'Combos', 'Pasta Combo', 135.00),
(56, 'Combos', 'Family Chicken Bundle', 499.00),
(57, 'Combos', 'Barkada Bundle', 699.00),
(58, 'Combos', 'Sweet Treats Combo', 120.00),
(59, 'Combos', 'Pinoy Classic Combo', 150.00),
(60, 'Combos', 'Ultimate Meal Box', 199.00),
(61, 'Combos', 'Breakfast Combo', 135.00),
(62, 'Combos', 'Dessert Lovers Box', 180.00);

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `items` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`items`)),
  `total` decimal(10,2) NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `items`, `total`, `status`, `created_at`) VALUES
(1, '[{\"name\": \"Barkada Bundle\", \"unit_price\": 699.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 699.0}, {\"name\": \"Blueberry Muffin\", \"unit_price\": 55.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 55.0}, {\"name\": \"Longsilog (Longganisa + Egg + Rice)\", \"unit_price\": 105.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 105.0}]', 859.00, 'served', '2025-10-06 22:28:24'),
(2, '[{\"name\": \"Blueberry Muffin\", \"unit_price\": 49.5, \"qty\": 1, \"size\": \"S\", \"subtotal\": 49.5}, {\"name\": \"Leche Flan\", \"unit_price\": 66.0, \"qty\": 1, \"size\": \"L\", \"subtotal\": 66.0}, {\"name\": \"Longsilog (Longganisa + Egg + Rice)\", \"unit_price\": 94.5, \"qty\": 1, \"size\": \"S\", \"subtotal\": 94.5}]', 210.00, 'served', '2025-10-06 23:50:07'),
(3, '[{\"name\": \"Spaghetti Bolognese\", \"unit_price\": 95.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 95.0}, {\"name\": \"Spaghetti Bolognese\", \"unit_price\": 85.5, \"qty\": 1, \"size\": \"S\", \"subtotal\": 85.5}, {\"name\": \"Spaghetti Bolognese\", \"unit_price\": 114.0, \"qty\": 1, \"size\": \"L\", \"subtotal\": 114.0}]', 294.50, 'served', '2025-10-06 23:52:20'),
(4, '[{\"name\": \"Cappuccino\", \"unit_price\": 58.5, \"qty\": 1, \"size\": \"S\", \"subtotal\": 58.5}, {\"name\": \"Iced Coffee\", \"unit_price\": 54.0, \"qty\": 1, \"size\": \"L\", \"subtotal\": 54.0}, {\"name\": \"Chicken BBQ Meal\", \"unit_price\": 112.5, \"qty\": 1, \"size\": \"S\", \"subtotal\": 112.5}, {\"name\": \"Longsilog (Longganisa + Egg + Rice)\", \"unit_price\": 105.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 105.0}]', 330.00, 'served', '2025-10-07 00:04:55'),
(5, '[{\"menu_id\": 1, \"name\": \"Cheeseburger\", \"unit_price\": 119.0, \"qty\": 1, \"size\": \"L\", \"subtotal\": 119.0}, {\"menu_id\": 1, \"name\": \"Cheeseburger\", \"unit_price\": 99.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 99.0}, {\"menu_id\": 1, \"name\": \"Cheeseburger\", \"unit_price\": 109.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 109.0}]', 327.00, 'served', '2025-10-07 00:17:31'),
(6, '[{\"menu_id\": 53, \"name\": \"Burger Combo Meal\", \"unit_price\": 155.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 155.0}, {\"menu_id\": 48, \"name\": \"Banana Split\", \"unit_price\": 95.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 95.0}]', 250.00, 'served', '2025-10-07 00:36:12'),
(7, '[{\"menu_id\": 47, \"name\": \"Choco Lava Cake\", \"unit_price\": 105.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 105.0}]', 105.00, 'served', '2025-10-07 00:36:24'),
(8, '[{\"menu_id\": 29, \"name\": \"Coca-Cola in Can\", \"unit_price\": 35.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 35.0}, {\"menu_id\": 25, \"name\": \"Longsilog (Longganisa + Egg + Rice)\", \"unit_price\": 115.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 115.0}, {\"menu_id\": 2, \"name\": \"Fried Chicken\", \"unit_price\": 120.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 120.0}]', 270.00, 'served', '2025-10-07 00:36:45'),
(9, '[{\"menu_id\": 61, \"name\": \"Breakfast Combo\", \"unit_price\": 135.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 135.0}, {\"menu_id\": 55, \"name\": \"Pasta Combo\", \"unit_price\": 135.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 135.0}, {\"menu_id\": 60, \"name\": \"Ultimate Meal Box\", \"unit_price\": 199.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 199.0}]', 469.00, 'served', '2025-10-07 00:45:49'),
(10, '[{\"menu_id\": 38, \"name\": \"Fruit Shake (Watermelon)\", \"unit_price\": 70.0, \"qty\": 5, \"size\": \"S\", \"subtotal\": 350.0}]', 350.00, 'served', '2025-10-07 00:46:02'),
(11, '[{\"menu_id\": 53, \"name\": \"Burger Combo Meal\", \"unit_price\": 155.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 155.0}, {\"menu_id\": 55, \"name\": \"Pasta Combo\", \"unit_price\": 135.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 135.0}, {\"menu_id\": 28, \"name\": \"Chicken BBQ Meal\", \"unit_price\": 125.0, \"qty\": 4, \"size\": \"S\", \"subtotal\": 500.0}, {\"menu_id\": 20, \"name\": \"Chicken Teriyaki Bowl\", \"unit_price\": 140.0, \"qty\": 2, \"size\": \"S\", \"subtotal\": 280.0}, {\"menu_id\": 21, \"name\": \"Grilled Liempo Rice Meal\", \"unit_price\": 150.0, \"qty\": 2, \"size\": \"S\", \"subtotal\": 300.0}, {\"menu_id\": 18, \"name\": \"Pork Sisig with Egg\", \"unit_price\": 130.0, \"qty\": 2, \"size\": \"S\", \"subtotal\": 260.0}, {\"menu_id\": 22, \"name\": \"Spaghetti Bolognese\", \"unit_price\": 95.0, \"qty\": 2, \"size\": \"S\", \"subtotal\": 190.0}, {\"menu_id\": 3, \"name\": \"Coke\", \"unit_price\": 25.0, \"qty\": 5, \"size\": \"S\", \"subtotal\": 125.0}, {\"menu_id\": 34, \"name\": \"Bottled Water\", \"unit_price\": 20.0, \"qty\": 3, \"size\": \"S\", \"subtotal\": 60.0}]', 2005.00, 'served', '2025-10-07 03:18:30'),
(12, '[{\"menu_id\": 62, \"name\": \"Dessert Lovers Box\", \"unit_price\": 190.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 190.0}, {\"menu_id\": 57, \"name\": \"Barkada Bundle\", \"unit_price\": 709.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 709.0}, {\"menu_id\": 52, \"name\": \"Blueberry Muffin\", \"unit_price\": 65.0, \"qty\": 1, \"size\": \"M\", \"subtotal\": 65.0}, {\"menu_id\": 17, \"name\": \"Chicken Fillet Rice Bowl\", \"unit_price\": 110.0, \"qty\": 1, \"size\": \"S\", \"subtotal\": 110.0}]', 1074.00, 'served', '2025-10-07 03:57:02'),
(13, '[{\"menu_id\": 46, \"name\": \"Buko Pandan\", \"unit_price\": 60.0, \"qty\": 5, \"size\": \"S\", \"subtotal\": 300.0}, {\"menu_id\": 47, \"name\": \"Choco Lava Cake\", \"unit_price\": 95.0, \"qty\": 5, \"size\": \"S\", \"subtotal\": 475.0}, {\"menu_id\": 37, \"name\": \"Fruit Shake (Mango)\", \"unit_price\": 80.0, \"qty\": 5, \"size\": \"M\", \"subtotal\": 400.0}]', 1175.00, 'served', '2025-10-07 03:57:45'),
(14, '[{\"menu_id\": 4, \"name\": \"Iced Tea\", \"unit_price\": 30.0, \"qty\": 4, \"size\": \"S\", \"subtotal\": 120.0}]', 120.00, 'served', '2025-10-07 03:58:04'),
(15, '[{\"menu_id\": 35, \"name\": \"Milk Tea (Classic)\", \"unit_price\": 90.0, \"qty\": 2, \"size\": \"M\", \"subtotal\": 180.0}, {\"menu_id\": 15, \"name\": \"Cheesy Beef Burger\", \"unit_price\": 99.0, \"qty\": 2, \"size\": \"S\", \"subtotal\": 198.0}]', 378.00, 'served', '2025-10-07 03:58:38'),
(16, '[{\"menu_id\": 27, \"name\": \"Chopsuey with Rice\", \"unit_price\": 130.0, \"qty\": 3, \"size\": \"L\", \"subtotal\": 390.0}]', 390.00, 'pending', '2025-10-07 03:58:52');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `role` varchar(32) NOT NULL DEFAULT 'admin'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `role`) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `menus`
--
ALTER TABLE `menus`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `menus`
--
ALTER TABLE `menus`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=63;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
