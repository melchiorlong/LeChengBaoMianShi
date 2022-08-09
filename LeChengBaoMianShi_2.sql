with event_log_filtered as (
	select
		user_id,
    	trunc(dateadd(sec, event_timestamp, '1970-01-01')) as event_date
	from event_log
	where 1 = 1
		and event_date >= '2020-09-01'
		and event_date < '2020-10-01'
),
	user_play_times as (
		select
			user_id
		from event_log_filtered
		group by user_id
		having count(1) between 1000 and 1999
	)
select
	count(1) as user_cnt
from user_play_times
;

􏰽