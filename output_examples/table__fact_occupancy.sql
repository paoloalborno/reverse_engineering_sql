CREATE TABLE `fact_occupancy` (
  `voyage_id` int DEFAULT NULL,
  `ship_id` int DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `booked_passengers` int DEFAULT NULL,
  `occupancy_rate` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci