# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields


class ProjectDispatching(geo_model.GeoModel):
    _name = 'project.dispatching'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _compute_name(self):
        for rec in self:
            rec.name = rec.department_id.name
            if rec.department_id.manager_id:
                rec.name += ' - ' + rec.department_id.manager_id.name

            rec.name += ' - ' + rec.analytic_account_id.name

            if rec.task_id:
                rec.name += ' - ' + rec.task_id.name
            if rec.activity_id:
                rec.name += ' - ' + rec.activity_id.name

    def _get_default_completition(self):
        return 0

    @api.multi
    def _compute_issue_count(self):
        for obj in self:
            if obj.task_id:
                obj.issue_count = self.env['project.issue'].search_count([('task_id', '=', obj.task_id.id)])
            else:
                obj.issue_count = 0

    @api.multi
    @api.depends('analytic_account_id')
    def _get_project(self):
        for rec in self:
            if rec.analytic_account_id:
                rec.project_id = self.env['project.project'].search([('analytic_account_id', '=', rec.analytic_account_id.id)])

    @api.onchange('analytic_account_id', 'task_id')
    def _onchange_department_project_task(self):
        if not self.analytic_account_id_use_tasks:
            self.task_id = None
            self.activity_id = None

        if self.analytic_account_id and self.task_id:
            query = 'select max(percent_complete) from project_dispatching where analytic_account_id=%s and task_id=%s'
            self.env.cr.execute(query, (self.analytic_account_id.id, self.task_id.id,))
            res = self.env.cr.fetchone()
            if res and res[0] and res[0]>0:
                self.percent_complete = res[0]

        if self.task_id and self.datetime_start and self.datetime_stop:
            last_dispatch = self.search([('datetime_stop', '<', self.datetime_stop), ('task_id', '=', self.task_id.id)],
                                        limit=1,
                                        order='datetime_stop DESC')
            self.department_id = last_dispatch.department_id

    @api.onchange('date_start', 'date_stop')
    def _onchange_date_start_date_stop(self):
        if self.date_start:
            self.datetime_start = self.date_start + ' 12:00:00'
        if self.date_stop:
            self.datetime_stop = self.date_stop + ' 12:00:00'

    @api.onchange('all_day')
    def _onchange_all_day(self):
        if self.all_day is True:
            if self.datetime_start:
                self.date_start = self.datetime_start[:10]
            if self.datetime_stop:
                self.date_stop = self.datetime_stop[:10]

    @api.depends('task_id', 'datetime_start')
    def _compute_task_dispatching_count(self):
        if self.task_id:
            self.task_dispatching_count = 1 + self.search([('task_id', '=', self.task_id.id), ('datetime_start', '<', self.datetime_start)], count=True)
            self.total_task_dispatching_count = self.search([('task_id', '=', self.task_id.id), ('id', '!=', self.id)], count=True)
        else:
            self.task_dispatching_count = None
            self.total_task_dispatching_count = None

    @api.one
    def _compute_milestones_description(self):
        out = '<div> <hr/>'
        if self.task_id and self.task_id.milestone_ids and len(self.task_id.milestone_ids) > 0:
            ms_to_show = self.task_id.milestone_ids.filtered(lambda r: r.milestone_id.show_on_dispatching is True)
            for item in ms_to_show:
                if item.forecast_date:
                    out += '<h3>' + str(item.milestone_id.name) + ' FC: ' + datetime.datetime.strptime(item.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d.%m.%Y') + '</h3>'
                if item.actual_date:
                    out += '<h3>' + str(item.milestone_id.name) + ' AC: ' + datetime.datetime.strptime(item.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d.%m.%Y') + '</h3>'
                out += '<hr/>'
        out += '</div>'
        self.milestones_description = out

    @api.one
    def _compute_timesheets(self):
        acts = self.env['account.analytic.line'].search([('task_id', '=', self.task_id.id), ('date', '>=', self.datetime_start), ('date', '<=', self.datetime_stop)])
        self.effective_hours = 0.0
        if acts and len(acts) > 0:
            self.timesheet_activity_ids = acts
            self.effective_hours = sum([item.unit_amount for item in self.timesheet_activity_ids])

    def _search_shared_site(self, operator, value):
        if (operator == '=' and value == True) or (operator == '!=' and value == False):
            operator = 'in'
        elif (operator == '!=' and value == True) or (operator == '=' and value == False):
            operator = 'not in'
        else:
            return [('id', 'in', [])]

        query = """
            SELECT
                d.id
            FROM
                project_dispatching d
                LEFT JOIN project_task t ON t.id = d.task_id
                LEFT JOIN project_site_details s ON s.id = t.site_id
            WHERE
                s.sharing_site IS TRUE
        """
        self.env.cr.execute(query)
        items = self.env.cr.fetchall()
        res_ids = [item[0] for item in items]
        return [('id', operator, res_ids)]

    @api.multi
    @api.depends('department_id')
    def _compute_team_leader(self):
        for rec in self:
            if rec.department_id and rec.department_id.manager_id:
                rec.team_leader_id = rec.department_id.manager_id

    @api.multi
    @api.depends('all_day', 'datetime_start', 'datetime_stop')
    def _compute_from_to_string(self):
        for rec in self:
            if rec.all_day:
                rec.calc_datetime_start = datetime.datetime.strptime(rec.datetime_start, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d.%m.%Y')
                rec.calc_datetime_stop = datetime.datetime.strptime(rec.datetime_stop, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d.%m.%Y')
            else:
                rec.calc_datetime_start = datetime.datetime.strptime(rec.datetime_start, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d.%m.%Y %H:%M:%S')
                rec.calc_datetime_stop = datetime.datetime.strptime(rec.datetime_stop, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d.%m.%Y %H:%M:%S')

    @api.multi
    @api.depends('task_id', 'task_id')
    def _compute_site_details(self):
        for rec in self:
            if rec.task_id and rec.task_id.site_id:
                rec.site_geo_point = rec.task_id.site_id.geo_point
                rec.site_name = rec.task_id.site_id.name
                rec.site_pole_type = rec.task_id.site_id.pole_type
                rec.site_placement = rec.task_id.site_id.placement
                rec.site_tech_subtype_2g = rec.task_id.site_id.tech_subtype_2g
                rec.site_tech_subtype_3g = rec.task_id.site_id.tech_subtype_3g
                rec.site_tech_subtype_4g = rec.task_id.site_id.tech_subtype_4g
                rec.site_owner = rec.task_id.site_id.owner
                rec.site_construction_owner = rec.task_id.site_id.construction_owner
                rec.site_site_user_tma = rec.task_id.site_id.site_user_tma
                rec.site_site_user_h3a = rec.task_id.site_id.site_user_h3a
                rec.site_arge = rec.task_id.site_id.arge
                rec.site_sharing_site = rec.task_id.site_id.sharing_site
                rec.site_longitude = rec.task_id.site_id.longitude
                rec.site_latitude = rec.task_id.site_id.latitude
                rec.site_district = rec.task_id.site_id.district
                rec.site_postcode = rec.task_id.site_id.postcode
                rec.site_city = rec.task_id.site_id.city
                rec.site_street = rec.task_id.site_id.street
                rec.site_house_number = rec.task_id.site_id.house_number
                rec.site_federal_state_code = rec.task_id.site_id.federal_state_code
                rec.site_federal_state = rec.task_id.site_id.federal_state
                rec.site_telecom = rec.task_id.site_id.telecom

    site_geo_point = geo_fields.GeoPoint('Dispatching Location', compute=_compute_site_details)
    site_name = fields.Char('Name', compute=_compute_site_details)
    site_pole_type = fields.Char('Pole type', compute=_compute_site_details)
    site_placement = fields.Char('Placement', compute=_compute_site_details)
    site_tech_subtype_2g = fields.Char('2G Tech Subtype', compute=_compute_site_details)
    site_tech_subtype_3g = fields.Char('3G Tech Subtype', compute=_compute_site_details)
    site_tech_subtype_4g = fields.Char('4G Tech Subtype', compute=_compute_site_details)
    site_owner = fields.Char('Owner', compute=_compute_site_details)
    site_construction_owner = fields.Char('Construction owner', compute=_compute_site_details)
    site_site_user_tma = fields.Boolean('StandortNutzer TMA', compute=_compute_site_details)
    site_site_user_h3a = fields.Boolean('StandortNutzer H3A', compute=_compute_site_details)
    site_arge = fields.Boolean('ARGE', compute=_compute_site_details)
    site_sharing_site = fields.Boolean('Sharing site', compute=_compute_site_details, search=_search_shared_site)
    site_longitude = fields.Char('Longitude', compute=_compute_site_details)
    site_latitude = fields.Char('Latitude', compute=_compute_site_details)
    site_district = fields.Char('District', compute=_compute_site_details)
    site_postcode = fields.Char('Postcode', compute=_compute_site_details)
    site_city = fields.Char('City', compute=_compute_site_details)
    site_street = fields.Char('Street', compute=_compute_site_details)
    site_house_number = fields.Char('House number', compute=_compute_site_details)
    site_federal_state_code = fields.Char('Federal state code', compute=_compute_site_details)
    site_federal_state = fields.Char('Federal state', compute=_compute_site_details)
    site_telecom = fields.Char('Telecom', compute=_compute_site_details)

    name = fields.Char('Name', compute=_compute_name)
    department_id = fields.Many2one('hr.department', 'Department', required=True, track_visibility='onchange')
    team_leader_id = fields.Many2one('hr.employee', 'Team leader', compute=_compute_team_leader)
    project_id = fields.Many2one('project.project', 'Project', compute=_get_project)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Field of activity', required=True, track_visibility='onchange')
    analytic_account_id_use_tasks = fields.Boolean(related='analytic_account_id.use_tasks')
    activity_id = fields.Many2one('project.activity', 'Main activity', track_visibility='onchange')
    task_id = fields.Many2one('project.task', 'Task', domain="[('project_id', '=', project_id)]", track_visibility='onchange')
    date_start = fields.Date('From')
    date_stop = fields.Date('To')
    all_day = fields.Boolean('All day?', default=True)
    datetime_start = fields.Datetime('From', required=True, track_visibility='onchange')
    datetime_stop = fields.Datetime('To', required=True, track_visibility='onchange')
    calc_datetime_start = fields.Char('From', compute=_compute_from_to_string)
    calc_datetime_stop = fields.Char('To', compute=_compute_from_to_string)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', track_visibility='onchange')
    percent_complete = fields.Selection([(0, '0 %'),
                                        (25, '25 %'),
                                        (50, '50 %'),
                                        (75, '75 %'),
                                        (100, '100 %')], string='% Complete', track_visibility='onchange', default=_get_default_completition)
    info = fields.Html('Description')
    assigned_user_id = fields.Many2one('res.users', 'Assigned to', related='task_id.user_id', readonly=True)
    issue_count = fields.Integer('Issue count', compute=_compute_issue_count)
    total_task_dispatching_count = fields.Integer('Total Task Dispatchings Count', readonly=True, compute=_compute_task_dispatching_count)
    task_dispatching_count = fields.Integer('Task Dispatching Counter', readonly=True, compute=_compute_task_dispatching_count)
    milestones_description = fields.Html('Milestones', compute=_compute_milestones_description)
    timesheet_activity_ids = fields.One2many(comodel_name='account.analytic.line', inverse_name=None, string='Timesheet activities', compute=_compute_timesheets, readonly=True)
    effective_hours = fields.Float('Hours spent', compute=_compute_timesheets)

    @api.constrains('department_id', 'datetime_start', 'datetime_stop')
    def _check_dates(self):
        start = datetime.datetime.strptime(self.datetime_start, tools.DEFAULT_SERVER_DATETIME_FORMAT) if self.datetime_start else False
        end = datetime.datetime.strptime(self.datetime_stop, tools.DEFAULT_SERVER_DATETIME_FORMAT) if self.datetime_stop else False
        if start and end:
            if start > end:
                raise e.ValidationError('Starting date must be before ending date.')

        if self.all_day is True:
            self.env.cr.execute("""
                select
                    COUNT(*)
                from
                    project_dispatching pd
                where
                    pd.id <> %s
                      AND
                    department_id = %s
                      AND
                    (
                        (%s::TIMESTAMP::DATE <= pd.datetime_start::DATE AND %s::TIMESTAMP::DATE >= pd.datetime_start::DATE)
                          OR
                        (%s::TIMESTAMP::DATE <= pd.datetime_stop::DATE AND %s::TIMESTAMP::DATE >= pd.datetime_stop::DATE)
                          OR
                        (%s::TIMESTAMP::DATE >= pd.datetime_start::DATE AND %s::TIMESTAMP::DATE <= pd.datetime_stop::DATE)
                    )
            """, (self.id,
                  self.department_id.id,
                  self.datetime_start, self.datetime_stop,
                  self.datetime_start, self.datetime_stop,
                  self.datetime_start, self.datetime_stop))

        else:
            self.env.cr.execute("""
                select
                    COUNT(*)
                from
                    project_dispatching pd
                where
                    pd.id <> %s
                      AND
                    pd.department_id = %s
                      AND
                    (
                      (pd.all_day = true AND (
                            (%s::TIMESTAMP::DATE <= pd.datetime_start::DATE AND %s::TIMESTAMP::DATE >= pd.datetime_start::DATE)
                              OR
                            (%s::TIMESTAMP::DATE <= pd.datetime_stop::DATE AND %s::TIMESTAMP::DATE >= pd.datetime_stop::DATE)
                              OR
                            (%s::TIMESTAMP::DATE >= pd.datetime_start::DATE AND %s::TIMESTAMP::DATE <= pd.datetime_stop::DATE)
                      ))
                         OR
                      ((TIMESTAMP %s, TIMESTAMP %s) OVERLAPS (pd.datetime_start, pd.datetime_stop))
                    )

            """, (self.id,
                  self.department_id.id,
                  self.datetime_start, self.datetime_stop,
                  self.datetime_start, self.datetime_stop,
                  self.datetime_start, self.datetime_stop,
                  self.datetime_start, self.datetime_stop))

        count = self.env.cr.fetchone()[0]
        if count > 0:
            raise e.ValidationError(self.department_id.name + ' is already dispatched for selected period.')

    @api.multi
    def write(self, vals):
        if 'datetime_start' in vals:
            vals['date_start'] = vals['datetime_start'][:10]
        if 'datetime_stop' in vals:
            vals['date_stop'] = vals['datetime_stop'][:10]
        return super(ProjectDispatching, self).write(vals)

    def return_action_to_open_issues(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.dispatching').browse(cr, uid, ids[0], context)
        if obj.task_id:
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_issues', 'project_issues_show_action', context=context)
            res['context'] = context
            res['context'].update({'default_task_id': obj.task_id.id, 'default_project_id': obj.analytic_account_id.id})
            res['domain'] = [('task_id', '=', obj.task_id.id)]
            if 'group_by' in res['context']:
                del res['context']['group_by']
            return res
        else:
            return True

    def return_action_to_open_task_dispatchings(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.dispatching').browse(cr, uid, ids[0], context)
        if obj.task_id:
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_dispatching', 'action_project_dispatching', context=context)
            res['context'] = context
            res['context'].update({'default_task_id': obj.task_id.id, 'default_analytic_account_id': obj.analytic_account_id.id})
            res['domain'] = [('task_id', '=', obj.task_id.id), ('id', '!=', obj.id)]
            if 'group_by' in res['context']:
                del res['context']['group_by']
            return res
        else:
            return True