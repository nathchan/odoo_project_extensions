from openerp import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _compute_dispatching_count(self):
        for obj in self:
            self.dispatching_count = self.env['project.dispatching'].search_count([('task_id', '=', obj.id)])

    dispatching_ids = fields.One2many('project.dispatching', 'task_id', 'Dispatching')
    dispatching_count = fields.Integer('Dispatching count', compute=_compute_dispatching_count)

    def return_action_to_open_dispatching(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.task').browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_dispatching', 'action_project_dispatching', context=context)
        res['context'] = context
        res['context'].update({'default_task_id': obj.id, 'default_project_id': obj.project_id.id})
        res['domain'] = [('task_id', '=', obj.id)]
        if 'group_by' in res['context']:
            del res['context']['group_by']
        return res
