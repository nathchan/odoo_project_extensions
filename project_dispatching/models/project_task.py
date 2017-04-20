# -*- coding: utf-8 -*-

from openerp import models, fields, api

from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields

class Task(geo_model.GeoModel):
    _inherit = 'project.task'

    @api.multi
    def _compute_dispatching_count(self):
        for obj in self:
            self.dispatching_count = self.env['project.dispatching'].search_count([('task_id', '=', obj.id)])

    def _search_shared_site(self, operator, value):
        if (operator == '=' and value == True) or (operator == '!=' and value == False):
            operator = 'in'
        elif (operator == '!=' and value == True) or (operator == '=' and value == False):
            operator = 'not in'
        else:
            return [('id', 'in', [])]

        query = """
            SELECT
                t.id
            FROM
                project_task t
                LEFT JOIN project_site_details s ON s.id = t.site_id
            WHERE
                s.sharing_site IS TRUE
        """
        self.env.cr.execute(query)
        items = self.env.cr.fetchall()
        res_ids = [item[0] for item in items]
        return [('id', operator, res_ids)]

    @api.multi
    @api.depends('site_id')
    def _compute_site_details(self):
        for rec in self:
            if rec.site_id:
                rec.site_geo_point = rec.site_id.geo_point
                rec.site_name = rec.site_id.name
                rec.site_pole_type = rec.site_id.pole_type
                rec.site_placement = rec.site_id.placement
                rec.site_tech_subtype_2g = rec.site_id.tech_subtype_2g
                rec.site_tech_subtype_3g = rec.site_id.tech_subtype_3g
                rec.site_tech_subtype_4g = rec.site_id.tech_subtype_4g
                rec.site_owner = rec.site_id.owner
                rec.site_construction_owner = rec.site_id.construction_owner
                rec.site_site_user_tma = rec.site_id.site_user_tma
                rec.site_site_user_h3a = rec.site_id.site_user_h3a
                rec.site_arge = rec.site_id.arge
                rec.site_sharing_site = rec.site_id.sharing_site
                rec.site_longitude = rec.site_id.longitude
                rec.site_latitude = rec.site_id.latitude
                rec.site_district = rec.site_id.district
                rec.site_postcode = rec.site_id.postcode
                rec.site_city = rec.site_id.city
                rec.site_street = rec.site_id.street
                rec.site_house_number = rec.site_id.house_number
                rec.site_federal_state_code = rec.site_id.federal_state_code
                rec.site_federal_state = rec.site_id.federal_state
                rec.site_telecom = rec.site_id.telecom

    site_id = fields.Many2one('project.site.details', string='Site')
    site_geo_point = geo_fields.GeoPoint('Task Location', compute=_compute_site_details)
    site_name = fields.Char('Name', compute=_compute_site_details)
    site_pole_type = fields.Char('Pole type', compute=_compute_site_details)
    site_placement = fields.Char('Placement', compute=_compute_site_details)
    site_tech_subtype_2g = fields.Char('2G Tech Subtype', compute=_compute_site_details)
    site_tech_subtype_3g = fields.Char('3G Tech Subtype', compute=_compute_site_details)
    site_tech_subtype_4g = fields.Char('4G Tech Subtype', compute=_compute_site_details)
    site_owner = fields.Char('Owner', compute=_compute_site_details)
    site_construction_owner = fields.Char('Construction owner', compute=_compute_site_details)
    site_site_user_tma = fields.Boolean('StandortNutzer TMA', compute=_compute_site_details)
    site_site_user_h3a = fields.Boolean('StandortNutzer H3A', compute=_compute_site_details)
    site_arge = fields.Boolean('ARGE', compute=_compute_site_details)
    site_sharing_site = fields.Boolean('Sharing site', compute=_compute_site_details, search=_search_shared_site)
    site_longitude = fields.Char('Longitude', compute=_compute_site_details)
    site_latitude = fields.Char('Latitude', compute=_compute_site_details)
    site_district = fields.Char('District', compute=_compute_site_details)
    site_postcode = fields.Char('Postcode', compute=_compute_site_details)
    site_city = fields.Char('City', compute=_compute_site_details)
    site_street = fields.Char('Street', compute=_compute_site_details)
    site_house_number = fields.Char('House number', compute=_compute_site_details)
    site_federal_state_code = fields.Char('Federal state code', compute=_compute_site_details)
    site_federal_state = fields.Char('Federal state', compute=_compute_site_details)
    site_telecom = fields.Char('Telecom', compute=_compute_site_details)

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
