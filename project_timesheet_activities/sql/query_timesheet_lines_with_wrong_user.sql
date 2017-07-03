select
 ts.id as timesheet,
 r.user_id as timesheet_user,
 l.user_id as line_user
from
 account_analytic_line l
 left join hr_timesheet_sheet_sheet ts on ts.id = l.timesheet_sheet_id
 left join hr_employee e on e.id = ts.employee_id
 left join resource_resource r on r.id = e.resource_id
where
 l.user_id != r.user_id
