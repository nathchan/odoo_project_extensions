-- View: public.iris_quick_view_sran

-- DROP VIEW public.iris_quick_view_sran;

CREATE OR REPLACE VIEW public.iris_quick_view_sran AS
 SELECT pt.name AS customer_site_code,
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
          WHERE m.name::text = '1300'::text AND fc.task_id = pt.id) AS fc_1300,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1300'::text AND fc.task_id = pt.id) AS ac_1300,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1300'::text AND fc.task_id = pt.id) AS fc_yw_1300,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1300'::text AND fc.task_id = pt.id) AS ac_yw_1300,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1600'::text AND fc.task_id = pt.id) AS fc_1600,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1600'::text AND fc.task_id = pt.id) AS ac_1600,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1600'::text AND fc.task_id = pt.id) AS fc_yw_1600,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1600'::text AND fc.task_id = pt.id) AS ac_yw_1600,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1660'::text AND fc.task_id = pt.id) AS fc_1660,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1660'::text AND fc.task_id = pt.id) AS ac_1660,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1660'::text AND fc.task_id = pt.id) AS fc_yw_1660,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1660'::text AND fc.task_id = pt.id) AS ac_yw_1660,
    tg.name AS rollout_group,
    par.name AS assigned_to,
    scontra.name AS subcontractor,
        CASE
            WHEN pt.active IS TRUE THEN 'No'::text
            ELSE 'Yes'::text
        END AS archived,
    priority.name AS mdf_priority,
    pt.cw_work_package_code AS cw_work_package_id,
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
     LEFT JOIN res_users u ON u.id = pt.user_id
     LEFT JOIN res_partner par ON par.id = u.partner_id
     LEFT JOIN res_partner scontra ON scontra.id = pt.subcontractor_id
     LEFT JOIN project_task_priority priority ON priority.id = pt.priority_id
  WHERE ac.name::text = 'SRAN'::text;

ALTER TABLE public.iris_quick_view_sran
  OWNER TO odoo9;
GRANT ALL ON TABLE public.iris_quick_view_sran TO odoo9;
GRANT SELECT ON TABLE public.iris_quick_view_sran TO iris_report;
