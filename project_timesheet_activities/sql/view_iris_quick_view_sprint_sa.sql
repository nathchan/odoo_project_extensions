-- View: public.iris_quick_view_sprint_sa

-- DROP VIEW public.iris_quick_view_sprint_sa;

CREATE OR REPLACE VIEW public.iris_quick_view_sprint_sa AS
 SELECT pt.name AS customer_site_code,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0100'::text AND fc.task_id = pt.id) AS fc_0100,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0100'::text AND fc.task_id = pt.id) AS ac_0100,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0100'::text AND fc.task_id = pt.id) AS fc_yw_0100,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0100'::text AND fc.task_id = pt.id) AS ac_yw_0100,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0110'::text AND fc.task_id = pt.id) AS fc_0110,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0110'::text AND fc.task_id = pt.id) AS ac_0110,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0110'::text AND fc.task_id = pt.id) AS fc_yw_0110,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0110'::text AND fc.task_id = pt.id) AS ac_yw_0110,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0400'::text AND fc.task_id = pt.id) AS fc_0400,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0400'::text AND fc.task_id = pt.id) AS ac_0400,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0400'::text AND fc.task_id = pt.id) AS fc_yw_0400,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0400'::text AND fc.task_id = pt.id) AS ac_yw_0400,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0500'::text AND fc.task_id = pt.id) AS fc_0500,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0500'::text AND fc.task_id = pt.id) AS ac_0500,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0500'::text AND fc.task_id = pt.id) AS fc_yw_0500,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0500'::text AND fc.task_id = pt.id) AS ac_yw_0500,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0620'::text AND fc.task_id = pt.id) AS fc_0620,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0620'::text AND fc.task_id = pt.id) AS ac_0620,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0620'::text AND fc.task_id = pt.id) AS fc_yw_0620,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0620'::text AND fc.task_id = pt.id) AS ac_yw_0620,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0640'::text AND fc.task_id = pt.id) AS fc_0640,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0640'::text AND fc.task_id = pt.id) AS ac_0640,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0640'::text AND fc.task_id = pt.id) AS fc_yw_0640,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0640'::text AND fc.task_id = pt.id) AS ac_yw_0640,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0650'::text AND fc.task_id = pt.id) AS fc_0650,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0650'::text AND fc.task_id = pt.id) AS ac_0650,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0650'::text AND fc.task_id = pt.id) AS fc_yw_0650,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0650'::text AND fc.task_id = pt.id) AS ac_yw_0650,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0700'::text AND fc.task_id = pt.id) AS fc_0700,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0700'::text AND fc.task_id = pt.id) AS ac_0700,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0700'::text AND fc.task_id = pt.id) AS fc_yw_0700,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0700'::text AND fc.task_id = pt.id) AS ac_yw_0700,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0800'::text AND fc.task_id = pt.id) AS fc_0800,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0800'::text AND fc.task_id = pt.id) AS ac_0800,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0800'::text AND fc.task_id = pt.id) AS fc_yw_0800,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0800'::text AND fc.task_id = pt.id) AS ac_yw_0800,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0900'::text AND fc.task_id = pt.id) AS fc_0900,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0900'::text AND fc.task_id = pt.id) AS ac_0900,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0900'::text AND fc.task_id = pt.id) AS fc_yw_0900,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0900'::text AND fc.task_id = pt.id) AS ac_yw_0900,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0950'::text AND fc.task_id = pt.id) AS fc_0950,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0950'::text AND fc.task_id = pt.id) AS ac_0950,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0950'::text AND fc.task_id = pt.id) AS fc_yw_0950,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0950'::text AND fc.task_id = pt.id) AS ac_yw_0950,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1000'::text AND fc.task_id = pt.id) AS fc_1000,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1000'::text AND fc.task_id = pt.id) AS ac_1000,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1000'::text AND fc.task_id = pt.id) AS fc_yw_1000,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1000'::text AND fc.task_id = pt.id) AS ac_yw_1000,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1010'::text AND fc.task_id = pt.id) AS fc_1010,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1010'::text AND fc.task_id = pt.id) AS ac_1010,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1010'::text AND fc.task_id = pt.id) AS fc_yw_1010,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1010'::text AND fc.task_id = pt.id) AS ac_yw_1010,
    tg.name AS rollout_group,
    scontra.name AS subcontractor,
        CASE
            WHEN pt.active IS TRUE THEN 'No'::text
            ELSE 'Yes'::text
        END AS archived,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0081'::text AND fc.task_id = pt.id) AS fc_0081,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0081'::text AND fc.task_id = pt.id) AS ac_0081,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0081'::text AND fc.task_id = pt.id) AS fc_yw_0081,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0081'::text AND fc.task_id = pt.id) AS ac_yw_0081,
    priority.name AS mdf_priority,
    pt.sa_work_package_code AS sa_work_package_id,
        CASE
            WHEN pt.priority::text = '1'::text THEN 'Yes'::text
            ELSE 'No'::text
        END AS priority,
        CASE
            WHEN pt.kanban_state::text = 'blocked'::text THEN 'Yes'::text
            ELSE 'No'::text
        END AS task_blocked,
    pt.blocked_until
   FROM project_task pt
     LEFT JOIN project_project pp ON pp.id = pt.project_id
     LEFT JOIN account_analytic_account ac ON ac.id = pp.analytic_account_id
     LEFT JOIN project_task_group tg ON tg.id = pt.task_group_id
     LEFT JOIN res_partner scontra ON scontra.id = pt.subcontractor_id
     LEFT JOIN project_task_priority priority ON priority.id = pt.priority_id
  WHERE ac.name::text = 'Sprint SA'::text;

ALTER TABLE public.iris_quick_view_sprint_sa
  OWNER TO odoo9;
GRANT ALL ON TABLE public.iris_quick_view_sprint_sa TO odoo9;
GRANT SELECT ON TABLE public.iris_quick_view_sprint_sa TO iris_report;
