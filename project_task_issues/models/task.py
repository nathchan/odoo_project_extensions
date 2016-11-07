# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _compute_issue_count(self):
        for obj in self:
            self.issue_count = self.env['project.issue'].search_count([('task_id', '=', obj.id)])

    issue_ids = fields.One2many('project.issue', 'task_id', 'Issues')
    issue_count = fields.Integer('Issue count', compute=_compute_issue_count)


    def return_action_to_open_issues(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.task').browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_issues', 'project_issues_show_action', context=context)
        res['context'] = context
        res['context'].update({'default_task_id': ids[0], 'default_project_id': obj.project_id.id})
        res['domain'] = [('task_id', '=', ids[0])]
        del res['context']['group_by']
        return res
