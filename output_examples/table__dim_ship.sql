CREATE TABLE `dim_ship` (
  `ship_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  PRIMARY KEY (`ship_id`),
  KEY `company_id` (`company_id`),
  CONSTRAINT `dim_ship_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `dim_cruise_companies` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci