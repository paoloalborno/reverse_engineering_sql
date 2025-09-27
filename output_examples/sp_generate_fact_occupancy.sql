CREATE DEFINER=`windows_user`@`%` PROCEDURE `sp_generate_fact_occupancy`()
BEGIN
  TRUNCATE TABLE fact_occupancy;
  INSERT INTO fact_occupancy (voyage_id, ship_id, capacity, booked_passengers, occupancy_rate)
  SELECT v.voyage_id, v.ship_id, sh.capacity, COUNT(DISTINCT f.passenger_id),
         COUNT(DISTINCT f.passenger_id)/sh.capacity
  FROM dim_voyage v
  JOIN dim_ship sh ON v.ship_id = sh.ship_id
  LEFT JOIN dim_segment s ON s.voyage_id = v.voyage_id
  LEFT JOIN fact_bookings f ON f.segment_id = s.segment_id
  GROUP BY v.voyage_id, v.ship_id, sh.capacity;
END