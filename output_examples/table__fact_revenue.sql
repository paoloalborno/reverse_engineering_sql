CREATE TABLE `fact_revenue` (
  `voyage_id` int DEFAULT NULL,
  `ship_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `total_revenue` decimal(12,2) DEFAULT NULL,
  `currency` char(3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci