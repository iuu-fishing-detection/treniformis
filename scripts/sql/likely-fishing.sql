/* version-3 */
select a.mmsi as mmsi from
(
  SELECT
    mmsi,
    count(*) c_msg,
    sum (shiptype_text = 'Fishing') c_fishing,
    sum (shiptype_text = 'Fishing') / count(*) fishing_msg_ratio
  FROM (TABLE_DATE_RANGE([{normalize_table_name}.], TIMESTAMP('{start_date}'), TIMESTAMP('{end_date}')))
  WHERE
    type in (5, 24)
    and shiptype_text is not null
    and shiptype_text != 'Not available'
  GROUP EACH BY
    mmsi
  HAVING
    c_fishing > 10 and fishing_msg_ratio > .99
) a
JOIN EACH
(
  SELECT
    integer(mmsi) as mmsi, COUNT(*) AS c_pos
  FROM (TABLE_DATE_RANGE([{normalize_table_name}.], TIMESTAMP('{start_date}'), TIMESTAMP('{end_date}')))
  WHERE
    lat IS NOT NULL AND lon IS NOT NULL
    and mmsi not in (987357573,987357579,987357559,986737000,983712160,987357529) // helicopters
    and speed > .1
  GROUP BY
    mmsi
  HAVING
    c_pos > 500
) b
ON a.mmsi = b.mmsi