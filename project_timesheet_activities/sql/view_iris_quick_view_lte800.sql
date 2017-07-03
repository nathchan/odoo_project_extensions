-- View: public.iris_quick_view_lte800

-- DROP VIEW public.iris_quick_view_lte800;

CREATE OR REPLACE VIEW public.iris_quick_view_lte800 AS
 SELECT pt.name AS customer_site_code,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1042'::text AND fc.task_id = pt.id) AS fc_1042,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1042'::text AND fc.task_id = pt.id) AS ac_1042,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1042'::text AND fc.task_id = pt.id) AS fc_yw_1042,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1042'::text AND fc.task_id = pt.id) AS ac_yw_1042,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1045'::text AND fc.task_id = pt.id) AS fc_1045,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1045'::text AND fc.task_id = pt.id) AS ac_1045,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1045'::text AND fc.task_id = pt.id) AS fc_yw_1045,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1045'::text AND fc.task_id = pt.id) AS ac_yw_1045,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1053'::text AND fc.task_id = pt.id) AS fc_1053,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1053'::text AND fc.task_id = pt.id) AS ac_1053,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1053'::text AND fc.task_id = pt.id) AS fc_yw_1053,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1053'::text AND fc.task_id = pt.id) AS ac_yw_1053,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1060'::text AND fc.task_id = pt.id) AS fc_1060,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1060'::text AND fc.task_id = pt.id) AS ac_1060,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1060'::text AND fc.task_id = pt.id) AS fc_yw_1060,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1060'::text AND fc.task_id = pt.id) AS ac_yw_1060,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1080'::text AND fc.task_id = pt.id) AS fc_1080,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1080'::text AND fc.task_id = pt.id) AS ac_1080,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1080'::text AND fc.task_id = pt.id) AS fc_yw_1080,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1080'::text AND fc.task_id = pt.id) AS ac_yw_1080,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1100'::text AND fc.task_id = pt.id) AS fc_1100,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1100'::text AND fc.task_id = pt.id) AS ac_1100,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1100'::text AND fc.task_id = pt.id) AS fc_yw_1100,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1100'::text AND fc.task_id = pt.id) AS ac_yw_1100,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1200'::text AND fc.task_id = pt.id) AS fc_1200,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1200'::text AND fc.task_id = pt.id) AS ac_1200,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1200'::text AND fc.task_id = pt.id) AS fc_yw_1200,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1200'::text AND fc.task_id = pt.id) AS ac_yw_1200,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1202'::text AND fc.task_id = pt.id) AS fc_1202,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1202'::text AND fc.task_id = pt.id) AS ac_1202,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1202'::text AND fc.task_id = pt.id) AS fc_yw_1202,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1202'::text AND fc.task_id = pt.id) AS ac_yw_1202,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1235'::text AND fc.task_id = pt.id) AS fc_1235,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1235'::text AND fc.task_id = pt.id) AS ac_1235,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1235'::text AND fc.task_id = pt.id) AS fc_yw_1235,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1235'::text AND fc.task_id = pt.id) AS ac_yw_1235,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1260'::text AND fc.task_id = pt.id) AS fc_1260,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1260'::text AND fc.task_id = pt.id) AS ac_1260,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1260'::text AND fc.task_id = pt.id) AS fc_yw_1260,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1260'::text AND fc.task_id = pt.id) AS ac_yw_1260,
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
          WHERE m.name::text = '1650'::text AND fc.task_id = pt.id) AS fc_1650,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1650'::text AND fc.task_id = pt.id) AS ac_1650,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1650'::text AND fc.task_id = pt.id) AS fc_yw_1650,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1650'::text AND fc.task_id = pt.id) AS ac_yw_1650,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1700'::text AND fc.task_id = pt.id) AS fc_1700,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1700'::text AND fc.task_id = pt.id) AS ac_1700,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1700'::text AND fc.task_id = pt.id) AS fc_yw_1700,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '1700'::text AND fc.task_id = pt.id) AS ac_yw_1700,
    tg.name AS rollout_group,
    par.name AS assigned_to,
    scontra.name AS subcontractor,
        CASE
            WHEN pt.active IS TRUE THEN 'No'::text
            ELSE 'Yes'::text
        END AS archived,
    ( SELECT fc.forecast_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0082'::text AND fc.task_id = pt.id) AS fc_0082,
    ( SELECT fc.actual_date
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0082'::text AND fc.task_id = pt.id) AS ac_0082,
    ( SELECT fc.forecast_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0082'::text AND fc.task_id = pt.id) AS fc_yw_0082,
    ( SELECT fc.actual_week
           FROM project_task_milestone_forecast fc
             LEFT JOIN project_milestone m ON m.id = fc.milestone_id
          WHERE m.name::text = '0082'::text AND fc.task_id = pt.id) AS ac_yw_0082,
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
  WHERE ac.name::text = 'LTE800'::text;

ALTER TABLE public.iris_quick_view_lte800
  OWNER TO odoo9;
GRANT ALL ON TABLE public.iris_quick_view_lte800 TO odoo9;
GRANT SELECT ON TABLE public.iris_quick_view_lte800 TO iris_report;
