/*
 change created_dt/updated_dt to created_at/updated_at.
*/
alter table time_entries rename column created_dt to created_at;
alter table time_entries rename column updated_dt to updated_at;
alter table slimtimer_users rename column created_dt to created_at;
alter table slimtimer_users rename column updated_dt to updated_at;
