# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime



class ProjectTaskMilestoneForecast(models.Model):
    _name = 'project.task.milestone.forecast'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'milestone_id'
    _order = 'sequence_order'

    def _skip_date(self, date):
        if not isinstance(date, basestring):
            str_date = date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        else:
            str_date = date
        query = """
            select
                case when '%s' in (select date from hr_day_off)
                        then 1
                        else 0
                end as res
        """
        self.env.cr.execute(query % (str_date,))
        res = self.env.cr.fetchone()
        if res[0] == 1:
            return True
        else:
            return False

    @api.multi
    def _get_default_duration(self):
        for rec in self:
            rec.duration_days = rec.milestone_id.duration

    @api.multi
    def _get_name(self):
        for rec in self:
            rec.name = ''
            if rec.milestone_id:
                rec.name += 'Milestone ' + str(rec.milestone_id.name)
            if rec.task_id:
                rec.name += ' - Task ' + str(rec.task_id.name)

    @api.multi
    def _compute_issue_count(self):
        for obj in self:
            if obj.task_id:
                obj.issue_count = self.env['project.issue'].search([('task_id', '=', obj.task_id.id),
                                                                    ('milestone_id', '=', obj.id),
                                                                    '|',
                                                                    ('active', '=', True),
                                                                    ('active', '=', False)],
                                                                   count=True)
                obj.opened_issue_count = self.env['project.issue'].search([('task_id', '=', obj.task_id.id),
                                                                           ('milestone_id', '=', obj.id),
                                                                           ('active', '=', True)],
                                                                          count=True)
            else:
                obj.issue_count = 0
                obj.opened_issue_count = 0

    @api.multi
    @api.depends('forecast_date', 'actual_date')
    def _compute_weeks(self):
        for rec in self:
            if rec.forecast_date:
                fc = datetime.datetime.strptime(rec.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                week_no = fc.isocalendar()[1]
                week = str(week_no) if week_no > 9 else '0' + str(week_no)
                year = str(fc.isocalendar()[0]) + '-W'
                rec.forecast_week = year + week
            else:
                rec.forecast_week = False

            if rec.actual_date:
                ac = datetime.datetime.strptime(rec.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                week_no = ac.isocalendar()[1]
                week = str(week_no) if week_no > 9 else '0' + str(week_no)
                year = str(ac.isocalendar()[0]) + '-W'
                rec.actual_week = year + week
            else:
                rec.actual_week = False

    @api.multi
    def _compute_predecessors_forecast_actual(self):
        for rec in self:
            out = '<div> <hr/>'

            # find predecessors from tasks milestone template
            milestone_template = rec.task_id.milestone_template_id
            target_template_line = milestone_template.line_ids.filtered(lambda x: x.milestone_id.id == rec.milestone_id.id)
            predecessor_ids = None
            if milestone_template and len(target_template_line) > 0:
                predecessor_ids = target_template_line.predecessor_milestone_ids

            if self.milestone_id and predecessor_ids and len(predecessor_ids) > 0:
                for line in predecessor_ids:
                    item = self.search([('task_id', '=', self.task_id.id), ('milestone_id', '=', line.id)])
                    if item:
                        if item.forecast_date:
                            out += '<h3>' + str(item.milestone_id.name) + ' FC: ' + datetime.datetime.strptime(item.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d.%m.%Y') + '</h3>'
                        if item.actual_date:
                            out += '<h3>' + str(item.milestone_id.name) + ' AC: ' + datetime.datetime.strptime(item.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d.%m.%Y') + '</h3>'
                        out += '<hr/>'

            out += '</div>'
            rec.predecessors_forecast_actual = out

    @api.multi
    def _compute_same_week_tasks_count(self):
        for rec in self:
            if rec.forecast_date:
                sql = """ select
                            count(*)
                          from
                            project_task_milestone_forecast
                          where
                            id <> %s
                            --and active = true
                            and project_id = %s
                            and milestone_id = %s
                            and EXTRACT(YEAR FROM forecast_date) = EXTRACT(YEAR FROM DATE %s)
                            and EXTRACT(WEEK FROM forecast_date) = EXTRACT(WEEK FROM DATE %s)"""
                self.env.cr.execute(sql, (rec.id, rec.project_id.id, rec.milestone_id.id, rec.forecast_date, rec.forecast_date,))
                rec.same_week_tasks_count = self.env.cr.fetchone()[0]
            else:
                0

    @api.depends('task_id.user_id')
    @api.one
    def _compute_assigned_to_active(self):
        if self.task_id:
            if self.task_id.user_id:
                self.assigned_to = self.task_id.user_id
            else:
                self.assigned_to = False

            self.task_active = self.task_id.active

    @api.depends('forecast_date', 'actual_date')
    @api.multi
    def _fc_ac_holiday(self):
        for rec in self:
            if rec.forecast_date and self._skip_date(rec.forecast_date):
                rec.forecast_is_holiday = True
            else:
                rec.forecast_is_holiday = False
            if rec.actual_date and self._skip_date(rec.actual_date):
                rec.actual_is_holiday = True
            else:
                rec.actual_is_holiday = False

    active = fields.Boolean('Active', default=True)
    same_week_tasks_count = fields.Integer('Task FC in same week', compute=_compute_same_week_tasks_count)
    predecessors_forecast_actual = fields.Html('Predecessors', compute=_compute_predecessors_forecast_actual)
    issue_count = fields.Integer('Issue Count', compute=_compute_issue_count)
    opened_issue_count = fields.Integer('Opened Issue Count', compute=_compute_issue_count)
    project_id = fields.Many2one('project.project', 'Project', required=True, track_visibility='onchange')
    task_id = fields.Many2one('project.task', 'Task', required=True, ondelete='cascade', track_visibility='onchange')
    task_active = fields.Boolean('Task Active', compute=_compute_assigned_to_active, store=True)
    assigned_to = fields.Many2one('res.users', 'Assigned to', compute=_compute_assigned_to_active, store=True)
    sequence_order = fields.Integer('Sequence')

    milestone_id = fields.Many2one('project.milestone', 'Milestone', required=True, ondelete='restrict', track_visibility='onchange')

    force_update = fields.Boolean('Force update', default=False)
    forecast_date_type = fields.Selection([('blocked_until', 'Blocked until'),
                                           ('must_start_on', 'Must start on')],
                                          'Constrain type',
                                          track_visibility='onchange')
    blocked_until_date = fields.Date('Blocked until')
    forecast_date = fields.Date('Forecast date', track_visibility='onchange')
    forecast_week = fields.Char('Forecast week', track_visibility='onchange', compute=_compute_weeks, store=True)
    forecast_is_holiday = fields.Boolean('FC is holiday', compute=_fc_ac_holiday)
    actual_date = fields.Date('Actual date', track_visibility='onchange')
    actual_week = fields.Char('Actual week', track_visibility='onchange', compute=_compute_weeks, store=True)
    actual_is_holiday = fields.Boolean('AC is holiday', compute=_fc_ac_holiday)

    name = fields.Char('Name', compute=_get_name)

    baseline_duration = fields.Integer('Baseline duration', default=_get_default_duration, group_operator="avg", track_visibility='onchange')
    duration_forecast = fields.Integer('Duration forecast', default=_get_default_duration, group_operator="avg", track_visibility='onchange')

    kanban_state = fields.Selection([('normal', 'In Progress'),
                                     ('done', 'Ready for next stage'),
                                     ('blocked', 'Blocked')], 'Kanban State',
                                    track_visibility='onchange',
                                    default="normal",
                                    required=True,
                                    copy=False)

    _sql_constraints = [
        ('unique_task_milestone', 'unique(task_id, milestone_id)', 'Combination of task and milestone must be unique!')
    ]

    def calculate_forecast(self):
        self.ensure_one()

        future_milestones = self.env['project.task.milestone.forecast'].search([('task_id', '=', self.task_id.id),
                                                                                ('project_id', '=', self.project_id.id),
                                                                                ('sequence_order', '>', self.sequence_order)],
                                                                               order='sequence_order')

        if len(future_milestones) == 0:
            return True

        if self.actual_date:
            start_date = datetime.datetime.strptime(self.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        elif self.forecast_date:
            start_date = datetime.datetime.strptime(self.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        else:
            raise e.ValidationError('Task: '+self.task_id.name+'\nMilestone: '+self.milestone_id.name+'\nFirst enter Forecast date or Actual date, please.')

        for milestone in future_milestones:

            if milestone.actual_date:
                start_date = datetime.datetime.strptime(milestone.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                continue

            if milestone.forecast_date_type == 'must_start_on' and milestone.forecast_date:
                start_date = datetime.datetime.strptime(milestone.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                continue

            # find predecessors from tasks milestone template
            milestone_template = self.task_id.milestone_template_id
            target_template_line = milestone_template.line_ids.filtered(lambda x: x.milestone_id.id == milestone.milestone_id.id)
            predecessor_ids = None
            if milestone_template and len(target_template_line) > 0:
                predecessor_ids = target_template_line.predecessor_milestone_ids

            if predecessor_ids and len(predecessor_ids) > 0:
                dates = []
                all_milestones = self.env['project.task.milestone.forecast'].search([('task_id', '=', self.task_id.id),
                                                                                     ('project_id', '=', self.project_id.id)],
                                                                                    order='sequence_order')
                for item in predecessor_ids:
                    predecessor = all_milestones.filtered(lambda r: r.milestone_id.id == item.id)
                    if predecessor and len(predecessor) == 1:
                        dates.append(predecessor.forecast_date)

                if len(dates) > 1:
                    current_date = max(datetime.datetime.strptime(date, tools.DEFAULT_SERVER_DATE_FORMAT) for date in dates)
                else:
                    current_date = start_date

            else:
                current_date = start_date

            # TODO: recalculate duration forecast based on issues related to task/milestone
            business_days_to_add = milestone.duration_forecast

            while business_days_to_add > 0:
                current_date += datetime.timedelta(days=1)
                if self._skip_date(current_date):
                    continue
                business_days_to_add -= 1

            if milestone.forecast_date_type == 'blocked_until' and milestone.forecast_date and milestone.blocked_until_date:
                if current_date < datetime.datetime.strptime(milestone.blocked_until_date, tools.DEFAULT_SERVER_DATE_FORMAT):
                    current_date = datetime.datetime.strptime(milestone.blocked_until_date, tools.DEFAULT_SERVER_DATE_FORMAT)

            data = {
                'force_update': True,
                'forecast_date': current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
            }
            milestone.write(data)
            start_date = current_date


    @api.multi
    def write(self, vals):
        date_seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7))
        if self.env.user.id != tools.SUPERUSER_ID:

            if 'forecast_date' in vals and vals['forecast_date'] is not False \
                    and 'duration_forecast' in vals and vals['duration_forecast'] is not False \
                    and ('force_update' not in vals or vals['force_update'] is False):

                raise e.ValidationError('Forecast date end and Duration forecast updated together and system can not \
                                determine which value to use for calculation of future forecasts. Please discard current \
                                changes and update only one of these two fields.')

            if 'actual_date' in vals and vals['actual_date'] is not False\
                    and ('force_update' not in vals or vals['force_update'] is False):
                opened_issues = self.env['project.issue'].search([('task_id', '=', self.task_id.id),
                                                                  ('milestone_id', '=', self.id),
                                                                  ('active', '=', True)], count=True)
                if opened_issues > 0:
                    raise e.ValidationError('There is one or more opened issues related to this milestone. Please \
                            close all issues before setting Actual date.')

                if datetime.datetime.strptime(vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT) > datetime.datetime.now():
                    raise e.ValidationError('Actual date can not be date in future.')

                if datetime.datetime.strptime(vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT) <= date_seven_days_ago:
                    raise e.ValidationError('Actual date can not be older than 7 days.')

                if 'forecast_date' in vals:
                    forecast = vals['forecast_date']
                else:
                    forecast = self.forecast_date

                fc_date = datetime.datetime.strptime(forecast, tools.DEFAULT_SERVER_DATE_FORMAT)
                ac_date = datetime.datetime.strptime(vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT)

                # if ac_date > fc_date:
                    # if self.issue_count < 1:
                    #     raise e.ValidationError('There is no Issues related to this milestone. \
                    #             First enter at least one Issue to explain postponement, please.')

                if fc_date != ac_date:
                    if ac_date > fc_date:
                        business_days_to_add = 0
                        current_date = fc_date
                        while True:
                            current_date += datetime.timedelta(days=1)

                            if self._skip_date(current_date) and current_date != ac_date:
                                continue
                            business_days_to_add += 1
                            if current_date == ac_date:
                                break
                        vals['duration_forecast'] = self.duration_forecast + business_days_to_add
                    else:
                        business_days_to_add = 0
                        current_date = fc_date
                        while True:
                            current_date -= datetime.timedelta(days=1)

                            if self._skip_date(current_date) and current_date != ac_date:
                                continue
                            business_days_to_add += 1
                            if current_date == ac_date:
                                break
                        days = self.duration_forecast - business_days_to_add
                        vals['duration_forecast'] = days if days >= 0 else 0

                self.env['project.task.milestone.update.log'].create({
                    'timestamp': datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
                    'milestone_line_id': self.id,
                    'updated_field': 'actual'
                })
                return super(ProjectTaskMilestoneForecast, self).write(vals)

            if 'forecast_date' in vals and vals['forecast_date'] is not False\
                    and ('duration_forecast' not in vals or vals['duration_forecast'] is False) \
                    and ('force_update' not in vals or vals['force_update'] is False):
                if self.forecast_date:
                    old_date = datetime.datetime.strptime(self.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                else:
                    old_date = datetime.datetime.strptime(vals['forecast_date'], tools.DEFAULT_SERVER_DATE_FORMAT)
                new_date = datetime.datetime.strptime(vals['forecast_date'], tools.DEFAULT_SERVER_DATE_FORMAT)

                if new_date <= date_seven_days_ago:
                    raise e.ValidationError('Forecast date can not be older than 7 days.')

                if old_date != new_date:
                    recalculate = True
                    end_date = new_date
                    if new_date > old_date:
                        # if self.issue_count < 1:
                        #     raise e.ValidationError('There is no Issues related to this milestone ['+self.milestone_id.name+']. \
                        #             First enter at least one Issue to explain postponement, please.')


                        business_days_to_add = 0
                        current_date = old_date
                        while True:
                            current_date += datetime.timedelta(days=1)

                            if self._skip_date(current_date) and current_date != new_date:
                                continue
                            business_days_to_add += 1
                            if current_date == new_date:
                                break
                        vals['duration_forecast'] = self.duration_forecast + business_days_to_add
                    else:
                        business_days_to_add = 0
                        current_date = old_date
                        while True:
                            current_date -= datetime.timedelta(days=1)

                            if self._skip_date(current_date) and current_date != new_date:
                                continue
                            business_days_to_add += 1
                            if current_date == new_date:
                                break
                        days = self.duration_forecast - business_days_to_add
                        vals['duration_forecast'] = days if days >= 0 else 0

            elif 'duration_forecast' in vals and vals['duration_forecast'] is not False \
                    and ('forecast_date' not in vals or vals['forecast_date'] is False)\
                    and ('force_update' not in vals or vals['force_update'] is False):
                if self.duration_forecast:
                    old_duration = self.duration_forecast
                else:
                    old_duration = 0
                new_duration = vals['duration_forecast']
                days_diff = new_duration - old_duration

                # if self.task_id and self.milestone_id and self.project_id:
                    # issue_count = self.env['project.issue'].search([('task_id', '=', self.task_id.id),
                    #                                                 ('milestone_id', '=', self.id),
                    #                                                 ('project_id', '=', self.project_id.id),
                    #                                                 '|',
                    #                                                 ('active', '=', True),
                    #                                                 ('active', '=', False)], count=True)
                    # if days_diff > 0 and issue_count < 1:
                    #     raise e.ValidationError('There is no Issues related to this milestone. First enter at least one Issue to explain postponement, please.')

                if days_diff != 0:
                    recalculate = True
                    operation = 'plus' if days_diff > 0 else 'minus'
                    # add days
                    business_days_to_add = abs(days_diff)
                    current_date = datetime.datetime.strptime(self.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                    while business_days_to_add > 0:
                        if operation == 'plus':
                            current_date += datetime.timedelta(days=1)
                        else:
                            current_date -= datetime.timedelta(days=1)

                        if self._skip_date(current_date):
                            continue
                        business_days_to_add -= 1
                    vals['forecast_date'] = current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
                    end_date = current_date
        if 'forecast_date' in vals:
            self.env['project.task.milestone.update.log'].create({
                'timestamp': datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
                'milestone_line_id': self.id,
                'updated_field': 'forecast'
            })
        if 'actual_date' in vals:
            self.env['project.task.milestone.update.log'].create({
                'timestamp': datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
                'milestone_line_id': self.id,
                'updated_field': 'actual'
            })
        return super(ProjectTaskMilestoneForecast, self).write(vals)

    def return_action_to_open_issues(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_issues', 'project_issues_show_action', context=context)
        res['context'] = context
        res['context'].update({'default_project_id': obj.project_id.id,
                               'default_task_id': obj.task_id.id,
                               'default_milestone_id': obj.id})
        res['domain'] = [('task_id', '=', obj.task_id.id),
                         ('milestone_id', '=', obj.id),
                         '|',
                         ('active', '=', True),
                         ('active', '=', False)]
        if 'group_by' in res['context']:
            del res['context']['group_by']
        return res
