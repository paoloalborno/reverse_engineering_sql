CREATE TABLE `fact_bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `passenger_id` int DEFAULT NULL,
  `segment_id` int DEFAULT NULL,
  `booking_date` date DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `passenger_id` (`passenger_id`),
  KEY `segment_id` (`segment_id`),
  CONSTRAINT `fact_bookings_ibfk_1` FOREIGN KEY (`passenger_id`) REFERENCES `dim_passenger` (`passenger_id`),
  CONSTRAINT `fact_bookings_ibfk_2` FOREIGN KEY (`segment_id`) REFERENCES `dim_segment` (`segment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci