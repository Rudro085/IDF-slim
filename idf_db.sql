-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 72.61.229.43:3307
-- Generation Time: Dec 31, 2025 at 03:36 PM
-- Server version: 9.5.0
-- PHP Version: 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `idf_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `id` int NOT NULL,
  `officer_id` int NOT NULL,
  `taxpayer_name` text NOT NULL,
  `taxpayer_tin` text NOT NULL,
  `status` text NOT NULL,
  `msg` text,
  `date_time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `statements`
--

CREATE TABLE `statements` (
  `id` int NOT NULL,
  `request_id` int NOT NULL,
  `pdf_name` text NOT NULL,
  `bank_name` text NOT NULL,
  `acc_no` text,
  `acc_type` text,
  `opening_balance` float DEFAULT NULL,
  `closing_balance` float DEFAULT NULL,
  `tags` text,
  `from_year` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `to_year` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `summery`
--

CREATE TABLE `summery` (
  `id` int NOT NULL,
  `request_id` int NOT NULL,
  `statement_id` int NOT NULL,
  `pdf_name` text NOT NULL,
  `bank_name` text NOT NULL,
  `acc_no` text NOT NULL,
  `acc_type` text NOT NULL,
  `fiscal_year` text NOT NULL,
  `total_debit` text NOT NULL,
  `total_credit` text NOT NULL,
  `credit_interest` text NOT NULL,
  `source_tax` text NOT NULL,
  `yearend_balance` text NOT NULL,
  `total_cash` text NOT NULL,
  `total_transfer` text NOT NULL,
  `total_cheque` text NOT NULL,
  `total_others` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int NOT NULL,
  `request_id` int NOT NULL,
  `statement_id` int NOT NULL,
  `date` text NOT NULL,
  `fiscal_year` text NOT NULL,
  `transaction_code` text NOT NULL,
  `details` text NOT NULL,
  `ref` text NOT NULL,
  `cheque` text NOT NULL,
  `debit` text NOT NULL,
  `credit` text NOT NULL,
  `balance` text NOT NULL,
  `tags` text,
  `Cat_L1` int DEFAULT NULL,
  `Cat_L2` int DEFAULT NULL,
  `Cat_L3` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `statements`
--
ALTER TABLE `statements`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `summery`
--
ALTER TABLE `summery`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=154;

--
-- AUTO_INCREMENT for table `statements`
--
ALTER TABLE `statements`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=221;

--
-- AUTO_INCREMENT for table `summery`
--
ALTER TABLE `summery`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=240;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41896;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
