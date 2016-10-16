# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _compute_phone_call_count(self):
        for obj in self:
            self.phone_call_count = self.env['project.task.phone.call'].search_count([('task_id', '=', obj.id)])

    phone_call_ids = fields.One2many('project.task.phone.call', 'task_id', 'Phone calls')
    phone_call_count = fields.Integer('Phone call count', compute=_compute_phone_call_count)

    def return_action_to_open_phone_calls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.task.phone.call').browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_phone_calls', 'project_task_phone_call_show_action', context=context)
        res['context'] = context
        res['context'].update({'default_task_id': ids[0], 'default_user_id': uid})
        res['domain'] = [('task_id', '=', ids[0])]
        return res