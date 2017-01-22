# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskMaterialOrder(models.Model):
    _name = 'project.task.material.order'

    material = fields.Selection([('a_b_goods', 'A+B Goods'),
                                 ('c_goods', 'C Goods'),
                                 ('steel', 'Steel'),
                                 ('crane', 'Crane')], 'Material', required=True)

    partner_id = fields.Many2one('res.partner', 'Partner')
    ordered_date = fields.Date('Ordered on')
    delivery_forecast_date = fields.Date('Delivery forecast')
    delivery_actual_date = fields.Date('Delivery actual')
    iris_inbound_date = fields.Date('IRIS inbound')
    iris_outbound_date = fields.Date('IRIS outbound')
    order_number = fields.Char('Order number')

    task_id = fields.Many2one('project.task', 'Task', required=True)
