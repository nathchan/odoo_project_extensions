# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from datetime import datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    @api.depends('material_order_ids.delivery_forecast_date', 'material_order_ids.delivery_actual_date')
    def _compute_alerts(self):
        for rec in self:
            due_soon = False
            overdue = False
            material_line = self.env['project.task.material.order'].search([('task_id', '=', rec.id),
                                                                            ('delivery_forecast_date', '!=', False),
                                                                            ('delivery_actual_date', '=', False)],
                                                                           order='delivery_forecast_date DESC',
                                                                           limit=1)

            if material_line:
                forecast_date = datetime.strptime(material_line[0].delivery_forecast_date, tools.DEFAULT_SERVER_DATE_FORMAT)
                days = (forecast_date - datetime.today()).days
                if days > 0 and days <= 7:
                    due_soon = True
                elif days <= 0:
                    overdue = True
            rec.alert_material_order_due_soon = due_soon
            rec.alert_material_order_overdue = overdue

    material_order_ids = fields.One2many('project.task.material.order', 'task_id', 'Material orders')

    alert_material_order_due_soon = fields.Boolean('Material order due soon', compute=_compute_alerts, store=True)
    alert_material_order_overdue = fields.Boolean('Material order overdue', compute=_compute_alerts, store=True)

    cw_percent_complete = fields.Selection([('0', '0 %'),
                                            ('25', '25 %'),
                                            ('50', '50 %'),
                                            ('75', '75 %'),
                                            ('100', '100 %')], string='CW % Complete', default=0)

    a_goods_ordered_date = fields.Date('A Goods Ordered')
    b_goods_ordered_date = fields.Date('B Goods Ordered')
    c_goods_ordered_date = fields.Date('C Goods Ordered')

    planning_package = fields.Selection([(1, 'Planning package for equipment swap'),
                                         (2, 'Planning package small'),
                                         (3, 'Planning package medium'),
                                         (4, 'Planning package large')], 'Planning package')
    site_acquisition_package = fields.Selection([(1, 'Site acquisitions small'),
                                                 (2, 'Site acquisitions medium'),
                                                 (3, 'Site acquisitions large'),
                                                 (4, 'Site acquisitions for new construction')], 'SA package')

    civil_works_package = fields.Selection([(1, 'Rooftop site extension'),
                                            (2, 'New Rooftop Outdoor site'),
                                            (3, 'New Rooftop Indoor site'),
                                            (4, 'Greenfield site extension'),
                                            (5, 'New Greenfield Outdoor site'),
                                            (6, 'Moving sharing partner'),
                                            (7, 'Site deconstruction')], 'CW package')

    @api.model
    def create(self, vals):
        new = super(ProjectTask, self).create(vals)

        project_lte800 = self.env['project.project'].search([('name', '=', 'LTE800')])

        if len(project_lte800)>0:
            tmp_vals = {
                'task_id': new.id,
                'material': 'a_goods',
                'partner_id': self.env.ref('project_task_packages.partner_kelog').id
            }
            self.env['project.task.material.order'].create(tmp_vals)

            tmp_vals = {
                'task_id': new.id,
                'material': 'b_goods',
                'partner_id': self.env.ref('project_task_packages.partner_kelog').id
            }
            self.env['project.task.material.order'].create(tmp_vals)

            tmp_vals = {
                'task_id': new.id,
                'material': 'c_goods',
                'partner_id': self.env.ref('project_task_packages.partner_sonepar').id
            }
            self.env['project.task.material.order'].create(tmp_vals)

            tmp_vals = {
                'task_id': new.id,
                'material': 'steel',
                'partner_id': self.env.ref('project_task_packages.partner_for_steel').id
            }
            self.env['project.task.material.order'].create(tmp_vals)

            tmp_vals = {
                'task_id': new.id,
                'material': 'crane',
                'partner_id': self.env.ref('project_task_packages.partner_for_crane').id
            }
            self.env['project.task.material.order'].create(tmp_vals)

        return new
