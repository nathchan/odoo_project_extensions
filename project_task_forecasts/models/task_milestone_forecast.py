# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime


class ProjectTaskMilestoneForecast(models.Model):
    _name = 'project.task.milestone.forecast'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'milestone_id'

    @api.multi
    def _get_default_duration(self):
        for rec in self:
            rec.duration_days = rec.milestone_id.duration

    @api.multi
    @api.depends('forecast_date', 'duration_forecast')
    def _compute_forecast_start_date(self):
        for rec in self:
            if rec.forecast_date:
                business_days_to_add = rec.duration_forecast
                current_date = datetime.datetime.strptime(rec.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                while business_days_to_add > 0:
                    current_date -= datetime.timedelta(days=1)
                    weekday = current_date.weekday()
                    if weekday >= 5:
                        # sunday = 6
                        continue
                    business_days_to_add -= 1
                rec.forecast_start_date = current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

    # @api.one
    # @api.onchange('duration_forecast')
    # def _onchange_duration_forecast(self):
    #     if self.duration_forecast:
    #         old_duration = self.browse([('id', '=', self.id)]).duration_forecast
    #         new_duration = self.duration_forecast
    #         days_diff = new_duration - old_duration
    #         if days_diff != 0:
    #             operation = 'plus' if days_diff > 0 else 'minus'
    #             # add days
    #             business_days_to_add = abs(days_diff)
    #             current_date = datetime.datetime.strptime(self.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
    #             while business_days_to_add > 0:
    #                 if operation == 'plus':
    #                     current_date += datetime.timedelta(days=1)
    #                 else:
    #                     current_date -= datetime.timedelta(days=1)
    #
    #                 weekday = current_date.weekday()
    #                 if weekday >= 5:
    #                     # sunday = 6
    #                     continue
    #                 business_days_to_add -= 1
    #             self.forecast_date = current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

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
                                                                    ('milestone_id', '=', obj.milestone_id.id),
                                                                    '|',
                                                                    ('active', '=', True),
                                                                    ('active', '=', False)],
                                                                   count=True)
            else:
                obj.issue_count = 0

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

            if rec.actual_date:
                ac = datetime.datetime.strptime(rec.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                week_no = ac.isocalendar()[1]
                week = str(week_no) if week_no > 9 else '0' + str(week_no)
                year = str(ac.isocalendar()[0]) + '-W'
                rec.actual_week = year + week



    issue_count = fields.Integer('Issue Count', compute=_compute_issue_count)
    project_id = fields.Many2one('project.project', 'Project', required=True, track_visibility='onchange')
    task_id = fields.Many2one('project.task', 'Task', required=True, ondelete='cascade', track_visibility='onchange')
    sequence = fields.Integer('Sequence', related='milestone_id.sequence', store=True)

    milestone_id = fields.Many2one('project.milestone', 'Milestone', required=True, ondelete='restrict', track_visibility='onchange')

    force_update = fields.Boolean('Force update', default=False)
    forecast_date = fields.Date('Forecast end date', track_visibility='onchange')
    forecast_week = fields.Char('Forecast week', track_visibility='onchange', compute=_compute_weeks, store=True)
    actual_date = fields.Date('Actual end date', track_visibility='onchange')
    actual_week = fields.Char('Actual week', track_visibility='onchange', compute=_compute_weeks, store=True)

    name = fields.Char('Name', compute=_get_name)

    baseline_duration = fields.Integer('Baseline duration', default=_get_default_duration, group_operator="avg", track_visibility='onchange')
    duration_forecast = fields.Integer('Duration forecast', default=_get_default_duration, group_operator="avg", track_visibility='onchange')
    forecast_start_date = fields.Date('Forecast start date', compute=_compute_forecast_start_date, store=True)

    _sql_constraints = [
        ('unique_task_milestone', 'unique(task_id, milestone_id)', 'Combination of task and milestone must be unique!')
    ]


    @api.one
    def calculate_forecast(self, vals):
        future_milestones = self.env['project.task.milestone.forecast'].search([('task_id', '=', self.task_id.id),
                                                                                ('sequence', '>', self.sequence)],
                                                                               order='sequence')

        if len(future_milestones) == 0:
            return True

        if self.actual_date:
            start_date = datetime.datetime.strptime(self.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        elif self.forecast_date:
            start_date = datetime.datetime.strptime(self.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        else:
            e.ValidationError('First enter Forecast date or Actual date, please.')

        for milestone in future_milestones:

            if milestone.actual_date:
                start_date = datetime.datetime.strptime(milestone.actual_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                continue

            if milestone.milestone_id.predecessor_milestone_ids and len(milestone.milestone_id.predecessor_milestone_ids) > 0:
                dates = []
                all_milestones = self.env['project.task.milestone.forecast'].search([('task_id', '=', self.task_id.id)],
                                                                                    order='sequence')
                for item in milestone.milestone_id.predecessor_milestone_ids:
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
                weekday = current_date.weekday()
                if weekday >= 5: # sunday = 6
                    continue
                business_days_to_add -= 1
            data = {
                'force_update': True,
                'forecast_date': current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
            }
            milestone.write(data)
            start_date = current_date


    @api.multi
    def write(self, vals):

        if 'forecast_date' in vals and vals['forecast_date'] is not False \
                and 'duration_forecast' in vals and vals['duration_forecast'] is not False:

            raise e.ValidationError('Forecast date end and Duration forecast updated together and system can not \
                            determine which value to use for calculation of future forecasts. Please discard current \
                            changes and update only one of these two fields.')

        if 'actual_date' in vals and vals['actual_date'] is not False:
            if 'forecast_date' in vals:
                forecast = vals['forecast_date']
            else:
                forecast = self.forecast_date

            fc_date = datetime.datetime.strptime(forecast, tools.DEFAULT_SERVER_DATE_FORMAT)
            ac_date = datetime.datetime.strptime(vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT)

            if fc_date.weekday() in [5, 6] or ac_date.weekday() in [5, 6]:
                raise e.ValidationError('Forecast or Actual date is Weekend day. Please choose another working day.')

            if ac_date > fc_date:
                if self.issue_count < 1:
                    raise e.ValidationError('There is no Issues related to this milestone. \
                            First enter at least one Issue to explain postponement, please.')

            if fc_date != ac_date:
                if ac_date > fc_date:
                    business_days_to_add = 0
                    current_date = fc_date
                    while True:
                        current_date += datetime.timedelta(days=1)

                        weekday = current_date.weekday()
                        if weekday >= 5:
                            # sunday = 6
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

                        weekday = current_date.weekday()
                        if weekday >= 5:
                            # sunday = 6
                            continue
                        business_days_to_add += 1
                        if current_date == ac_date:
                            break
                    days = self.duration_forecast - business_days_to_add
                    vals['duration_forecast'] = days if days >= 0 else 0

            return super(ProjectTaskMilestoneForecast, self).write(vals)

        if 'forecast_date' in vals and vals['forecast_date'] is not False\
                and ('duration_forecast' not in vals or vals['duration_forecast'] is False) \
                and ('force_update' not in vals or vals['force_update'] is False):
            if self.forecast_date:
                old_date = datetime.datetime.strptime(self.forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
            else:
                old_date = datetime.datetime.strptime(vals['forecast_date'], tools.DEFAULT_SERVER_DATE_FORMAT)
            new_date = datetime.datetime.strptime(vals['forecast_date'], tools.DEFAULT_SERVER_DATE_FORMAT)

            if new_date.weekday() in [5, 6] or old_date.weekday() in [5, 6]:
                raise e.ValidationError('Forecast date is Weekend day. Please choose another working day.')

            if old_date != new_date:
                recalculate = True
                end_date = new_date
                if new_date > old_date:
                    if self.issue_count < 1:
                        raise e.ValidationError('There is no Issues related to this milestone ['+self.milestone_id.name+']. \
                                First enter at least one Issue to explain postponement, please.')


                    business_days_to_add = 0
                    current_date = old_date
                    while True:
                        current_date += datetime.timedelta(days=1)

                        weekday = current_date.weekday()
                        if weekday >= 5:
                            # sunday = 6
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

                        weekday = current_date.weekday()
                        if weekday >= 5:
                            # sunday = 6
                            continue
                        business_days_to_add += 1
                        if current_date == new_date:
                            break
                    days = self.duration_forecast - business_days_to_add
                    vals['duration_forecast'] = days if days >= 0 else 0

        elif 'duration_forecast' in vals and vals['duration_forecast'] is not False \
                and ('forecast_date' not in vals or vals['forecast_date'] is False):
            if self.duration_forecast:
                old_duration = self.duration_forecast
            else:
                old_duration = 0
            new_duration = vals['duration_forecast']
            days_diff = new_duration - old_duration

            if self.task_id and self.milestone_id and self.project_id:
                issue_count = self.env['project.issue'].search([('task_id', '=', self.task_id.id),
                                                                ('milestone_id', '=', self.milestone_id.id),
                                                                ('project_id', '=', self.project_id.id),
                                                                '|',
                                                                ('active', '=', True),
                                                                ('active', '=', False)], count=True)
                if days_diff > 0 and issue_count < 1:
                    raise e.ValidationError('There is no Issues related to this milestone. First enter at least one Issue to explain postponement, please.')

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

                    weekday = current_date.weekday()
                    if weekday >= 5:
                        # sunday = 6
                        continue
                    business_days_to_add -= 1
                vals['forecast_date'] = current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
                end_date = current_date

        return super(ProjectTaskMilestoneForecast, self).write(vals)

    def return_action_to_open_issues(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_issues', 'project_issues_show_action', context=context)
        res['context'] = context
        res['context'].update({'default_task_id': obj.task_id.id,
                               'default_project_id': obj.project_id.id,
                               'default_milestone_id': obj.milestone_id.id})
        res['domain'] = [('task_id', '=', obj.task_id.id),
                         ('milestone_id', '=', obj.milestone_id.id),
                         '|',
                         ('active', '=', True),
                         ('active', '=', False)]
        if 'group_by' in res['context']:
            del res['context']['group_by']
        return res
