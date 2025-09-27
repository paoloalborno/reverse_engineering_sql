CREATE DEFINER=`windows_user`@`%` PROCEDURE `sp_generate_fact_bookings`()
BEGIN
  TRUNCATE TABLE fact_bookings;
  INSERT INTO fact_bookings (passenger_id, segment_id, booking_date, price)
  SELECT p.passenger_id, s.segment_id, CURDATE(), 100 + FLOOR(RAND()*900)
  FROM dim_passenger p
  JOIN dim_segment s ON 1=1
  WHERE RAND() < 0.15;
END