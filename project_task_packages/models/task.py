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

    @api.multi
    def _compute_filters(self):
        for rec in self:
            rec.filter_A_ordered_on = False
            rec.filter_B_ordered_on = False
            rec.filter_C_ordered_on = False
            rec.filter_STEEL_ordered_on = False
            rec.filter_CRANE_ordered_on = False
            rec.filter_A_B_inbound = False
            rec.filter_C_inbound = False
            rec.filter_STEEL_inbound = False
            rec.filter_CRANE_inbound = False
            rec.filter_A_B_outbound = False
            rec.filter_C_outbound = False
            rec.filter_STEEL_outbound = False
            rec.filter_CRANE_outbound = False

    material_order_ids = fields.One2many('project.task.material.order', 'task_id', 'Material orders')

    alert_material_order_due_soon = fields.Boolean('Material order due soon', compute=_compute_alerts, store=True)
    alert_material_order_overdue = fields.Boolean('Material order overdue', compute=_compute_alerts, store=True)

    cw_percent_complete = fields.Selection([('0', '0 %'),
                                            ('25', '25 %'),
                                            ('50', '50 %'),
                                            ('75', '75 %'),
                                            ('100', '100 %')], string='CW % Complete', default='0')

    # a_goods_ordered_date = fields.Date('A Goods Ordered')
    # b_goods_ordered_date = fields.Date('B Goods Ordered')
    # c_goods_ordered_date = fields.Date('C Goods Ordered')

    task_package_id = fields.Many2one('project.task.package', 'Task package')

    sa_work_package_code = fields.Char('SA WP ID')
    cw_work_package_code = fields.Char('CW WP ID')
    ti_work_package_code = fields.Char('TI WP ID')

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

    def _search_A_B_ordered_on(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'a_b_goods'),
                                                                                               ('ordered_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_C_ordered_on(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'c_goods'),
                                                                                               ('ordered_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_STEEL_ordered_on(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'steel'),
                                                                                               ('ordered_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_CRANE_ordered_on(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'crane'),
                                                                                               ('ordered_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_A_B_inbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'a_b_goods'),
                                                                                               ('iris_inbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_C_inbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'c_goods'),
                                                                                               ('iris_inbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_STEEL_inbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'steel'),
                                                                                               ('iris_inbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_CRANE_inbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'crane'),
                                                                                               ('iris_inbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_A_B_outbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'a_b_goods'),
                                                                                               ('iris_outbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_C_outbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'c_goods'),
                                                                                               ('iris_outbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_STEEL_outbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'steel'),
                                                                                               ('iris_outbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    def _search_CRANE_outbound(self, operator, value):
        new_operator = 'in'
        res_ids = [item.task_id.id for item in self.env['project.task.material.order'].search([('material', '=', 'crane'),
                                                                                               ('iris_outbound_date', operator, value)])]
        return [('id', new_operator, res_ids)]

    filter_A_B_ordered_on = fields.Date(string='A+B Ordered on', compute=_compute_filters, search=_search_A_B_ordered_on)
    filter_C_ordered_on = fields.Date(string='C Ordered on', compute=_compute_filters, search=_search_C_ordered_on)
    filter_STEEL_ordered_on = fields.Date(string='STEEL Ordered on', compute=_compute_filters, search=_search_STEEL_ordered_on)
    filter_CRANE_ordered_on = fields.Date(string='CRANE Ordered on', compute=_compute_filters, search=_search_CRANE_ordered_on)

    filter_A_B_inbound = fields.Date(string='A+B IRIS inbound', compute=_compute_filters, search=_search_A_B_inbound)
    filter_C_inbound = fields.Date(string='C IRIS inbound', compute=_compute_filters, search=_search_C_inbound)
    filter_STEEL_inbound = fields.Date(string='STEEL IRIS inbound', compute=_compute_filters, search=_search_STEEL_inbound)
    filter_CRANE_inbound = fields.Date(string='CRANE IRIS inbound', compute=_compute_filters, search=_search_CRANE_inbound)

    filter_A_B_outbound = fields.Date(string='A+B IRIS inbound', compute=_compute_filters, search=_search_A_B_inbound)
    filter_C_outbound = fields.Date(string='C IRIS inbound', compute=_compute_filters, search=_search_C_inbound)
    filter_STEEL_outbound = fields.Date(string='STEEL IRIS inbound', compute=_compute_filters, search=_search_STEEL_inbound)
    filter_CRANE_outbound = fields.Date(string='CRANE IRIS inbound', compute=_compute_filters, search=_search_CRANE_inbound)

    @api.model
    def create(self, vals):
        new = super(ProjectTask, self).create(vals)

        project_lte800 = self.env['project.project'].search([('name', '=', 'LTE800')])

        if len(project_lte800) > 0 and vals.get('project_id') and project_lte800[0].id == vals['project_id']:
            tmp_vals = {
                'task_id': new.id,
                'material': 'a_b_goods',
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
