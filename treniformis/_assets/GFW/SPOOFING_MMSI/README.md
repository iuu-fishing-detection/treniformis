# Spoofing MMSI Version 3

List of MMSIs that experience substantial ID spoofing

By ID spoofing, we mean two or more vessels that are using the same MMSI at the same time. 

All the messages for an MMSI are grouped into sets of tracks that are contiguous spatially and temporally.  
Each continuous track has a unique seg_id field added.  Some tracks contain invalid lan/lon (like 91, 181) and 
are put into a special 'BAD' segment. 

The test for spoofing is fairly naive - we simple compute the extent of each segment in time, add them all up, 
and compare that to the extent of time that the vessel is active.  If the segment time is longer than the 
active time, then we know that some of the segments must overlap, and this is the indication of ID spoofing.


Migration
---------

Files that were deleted during the migration from `vessel-lists`, but whose
content needs to be preserved.


### spoofing-mmsis-v3.sql ###

```sql
select mmsi from
(
SELECT
  a.mmsi AS mmsi,
  active_days,
  message_count,
  total_days,
  segment_count,
  segment_days,
  segment_days / LEAST(total_days, float(active_days)) AS spoof_ratio,
  segment_days - LEAST(total_days, float(active_days)) AS overlap_days,
  (segment_days - LEAST(total_days, float(active_days))) / LEAST(total_days, float(active_days)) AS spoof_percent,
  (segment_days / LEAST(total_days, float(active_days))) * (segment_days - LEAST(total_days, float(active_days))) as spoof_factor
FROM (
  SELECT
    mmsi,
    COUNT(*) AS active_days,
    SUM(message_count) AS message_count,
    (MAX(max_timestamp) - MIN(min_timestamp)) / 86400 AS total_days
  FROM (
    SELECT
      mmsi,
      UTC_USEC_TO_DAY(timestamp) AS day,
      COUNT(*) message_count,
      MIN(TIMESTAMP_TO_SEC(timestamp)) AS min_timestamp,
      MAX(TIMESTAMP_TO_SEC(timestamp)) AS max_timestamp
    FROM (TABLE_DATE_RANGE([pipeline_classify_logistic_661b.], TIMESTAMP('2015-01-01'), TIMESTAMP('2015-12-31')))
    WHERE
      RIGHT(seg_id, 3) != 'BAD'
    GROUP BY
      mmsi,
      day )
  GROUP BY
    mmsi ) a
JOIN (
  SELECT
    mmsi,
    COUNT(*) segment_count,
    SUM(max_timestamp - min_timestamp) / 86400 AS segment_days
  FROM (
    SELECT
      mmsi,
      COUNT(*) AS message_count,
      MIN(TIMESTAMP_TO_SEC(timestamp)) AS min_timestamp,
      MAX(TIMESTAMP_TO_SEC(timestamp)) AS max_timestamp
    FROM (TABLE_DATE_RANGE([pipeline_classify_logistic_661b.], TIMESTAMP('2015-01-01'), TIMESTAMP('2015-12-31')))
    WHERE
      RIGHT(seg_id, 3) != 'BAD'
    GROUP BY
      mmsi,
      seg_id )
  GROUP BY
    mmsi ) b
ON
  a.mmsi = b.mmsi
)
where active_days > 3 and spoof_percent > 0.01
```