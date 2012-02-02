/*
 add created_dt and updated_dt columns to slimtimer_users and time_entries tables
*/
alter table time_entries add column created_dt timestamp without time zone;
alter table time_entries add column updated_dt timestamp without time zone;
alter table slimtimer_users add column created_dt timestamp without time zone;
alter table slimtimer_users add column updated_dt timestamp without time zone;
