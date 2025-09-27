CREATE TABLE `dim_voyage` (
  `voyage_id` int NOT NULL AUTO_INCREMENT,
  `ship_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`voyage_id`),
  KEY `ship_id` (`ship_id`),
  CONSTRAINT `dim_voyage_ibfk_1` FOREIGN KEY (`ship_id`) REFERENCES `dim_ship` (`ship_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci