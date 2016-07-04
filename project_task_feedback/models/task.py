from openerp import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    feedback = fields.Selection([('interesting', 'Interesting task'),
                                 ('normal', 'Normal task'),
                                 ('stupid', 'Stupid task'),
                                 ], 'Feedback from employee', track_visibility='onchange')
