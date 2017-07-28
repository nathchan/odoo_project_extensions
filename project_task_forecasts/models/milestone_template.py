# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions as e


class MilestoneTemplate(models.Model):
    _name = 'project.milestone.template'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', required=True, track_visibility='onchange')
    line_ids = fields.One2many('project.milestone.template.line', 'milestone_template_id', string='Milestones')
    project_id = fields.Many2one('project.project', 'Project', required=True, track_visibility='onchange')
    is_default = fields.Boolean('Is default', track_visibility='onchange')
    info = fields.Text('Description', track_visibility='onchange')

    @api.constrains('is_default', 'project_id')
    def default_project_template_constrains(self):
        if self.is_default is True and self.project_id:
            if self.search([('is_default', '=', True), ('project_id', '=', self.project_id.id), ('id', '!=', self.id)], count=True) > 0:
                raise e.ValidationError('Only one default template can be in a project.')

    @api.one
    def update_milestones(self):
        err_msgs = []
        for task in self.env['project.task'].search([('milestone_template_id', '=', self.id)]):
            try:
                task.apply_milestone_template()
            except Exception as e:
                err_msgs.append(e.name)

        if len(err_msgs) > 0:
            raise e.UserError('\n\n\n'.join(err_msgs))
