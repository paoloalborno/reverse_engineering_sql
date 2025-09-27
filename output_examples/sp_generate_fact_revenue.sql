CREATE DEFINER=`windows_user`@`%` PROCEDURE `sp_generate_fact_revenue`()
BEGIN
  TRUNCATE TABLE fact_revenue;
  INSERT INTO fact_revenue (voyage_id, ship_id, company_id, total_revenue, currency)
  SELECT v.voyage_id, v.ship_id, sh.company_id, SUM(f.price), 'EUR'
  FROM fact_bookings f
  JOIN dim_segment s ON f.segment_id = s.segment_id
  JOIN dim_voyage v ON s.voyage_id = v.voyage_id
  JOIN dim_ship sh ON v.ship_id = sh.ship_id
  GROUP BY v.voyage_id, v.ship_id, sh.company_id;
END