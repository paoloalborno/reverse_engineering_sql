CREATE TABLE `dim_segment` (
  `segment_id` int NOT NULL AUTO_INCREMENT,
  `voyage_id` int DEFAULT NULL,
  `start_port_id` int DEFAULT NULL,
  `end_port_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`segment_id`),
  KEY `voyage_id` (`voyage_id`),
  KEY `start_port_id` (`start_port_id`),
  KEY `end_port_id` (`end_port_id`),
  CONSTRAINT `dim_segment_ibfk_1` FOREIGN KEY (`voyage_id`) REFERENCES `dim_voyage` (`voyage_id`),
  CONSTRAINT `dim_segment_ibfk_2` FOREIGN KEY (`start_port_id`) REFERENCES `dim_port` (`port_id`),
  CONSTRAINT `dim_segment_ibfk_3` FOREIGN KEY (`end_port_id`) REFERENCES `dim_port` (`port_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci