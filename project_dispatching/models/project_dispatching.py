# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime


class ProjectDispatching(models.Model):
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
        else:
            self.task_dispatching_count = None

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
        if acts and len(acts) > 0:
            self.timesheet_activity_ids = acts

    name = fields.Char('Name', compute=_compute_name)
    department_id = fields.Many2one('hr.department', 'Department', required=True, track_visibility='onchange')
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
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', track_visibility='onchange')
    percent_complete = fields.Selection([(0, '0 %'),
                                        (25, '25 %'),
                                        (50, '50 %'),
                                        (75, '75 %'),
                                        (100, '100 %')], string='% Complete', track_visibility='onchange', default=_get_default_completition)
    info = fields.Html('Description')
    assigned_user_id = fields.Many2one('res.users', 'Assigned to', related='task_id.user_id', readonly=True)
    issue_count = fields.Integer('Issue count', compute=_compute_issue_count)
    task_dispatching_count = fields.Integer('Task Dispatching Counter', readonly=True, compute=_compute_task_dispatching_count)
    milestones_description = fields.Html('Milestones', compute=_compute_milestones_description)
    timesheet_activity_ids = fields.One2many(comodel_name='account.analytic.line', inverse_name=None, string='Timesheet activities', compute=_compute_timesheets, readonly=True)

    @api.constrains('department_id', 'datetime_start', 'datetime_stop')
    def _check_dates(self):
        start = datetime.datetime.strptime(self.datetime_start, tools.DEFAULT_SERVER_DATETIME_FORMAT) if self.datetime_start else False
        end = datetime.datetime.strptime(self.datetime_stop, tools.DEFAULT_SERVER_DATETIME_FORMAT) if self.datetime_stop else False
        if start and end:
            if start > end:
                raise e.ValidationError('Starting date must be lower than ending date.')

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
