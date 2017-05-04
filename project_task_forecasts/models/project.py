# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions as ex


class ProjectProject(models.Model):
    _inherit = 'project.project'

    milestone_ids = fields.One2many('project.milestone', 'project_id', 'Milestones')
    project_code = fields.Char('Project ID')
    project_wp_code = fields.Char('DWP ID')

    @api.one
    def apply_milestones_template(self):
        sql = """
            select distinct
                task_id
            from
                project_task_milestone_forecast
            where
                project_id = %s
        """
        self.env.cr.execute(sql % (self.id, ))
        res_ids = self.env.cr.fetchall()
        err_msgs = []
        for task in self.env['project.task'].browse([item[0] for item in res_ids]):
            ms = task.milestone_ids.sorted(lambda x: x.sequence_order)[0]
            try:
                ms.calculate_forecast()
            except Exception as e:
                err_msgs.append(e.name)

        if len(err_msgs) > 0:
            raise ex.UserError('\n\n\n'.join(err_msgs))
