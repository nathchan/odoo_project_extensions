# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields
import geojson
from geojson import Point

class ProjectSiteDetails(geo_model.GeoModel):
    _name = 'project.site.details'
    _rec_name = 'number'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.one
    @api.onchange('longitude', 'latitude')
    def _compute_geo_point(self):
        if self.longitude and self.latitude:
            try:
                sql_query = """
                    SELECT
                        ST_X(ST_Transform( St_GeometryFromText('POINT(%s %s)', 4326), 900913)),
                        ST_Y(ST_Transform( St_GeometryFromText('POINT(%s %s)', 4326), 900913))
                """
                self.env.cr.execute(sql_query % (self.longitude, self.latitude, self.longitude, self.latitude))
                res = self.env.cr.fetchone()
                f_lon = float(res[0])
                f_lat = float(res[1])
                pt = Point((f_lon, f_lat))
                self.geo_point = geojson.dumps(pt)
            except:
                raise e.ValidationError('Wrong coordinate format.')

    @api.one
    @api.onchange('geo_point')
    def _compute_coordinates(self):
        if self.geo_point:
            pt = geojson.loads(self.geo_point)
            if pt.coordinates and len(pt.coordinates) == 2:
                sql_query = """
                    SELECT
                        ST_X(ST_Transform( St_GeometryFromText('POINT(%s %s)', 900913), 4326)),
                        ST_Y(ST_Transform( St_GeometryFromText('POINT(%s %s)', 900913), 4326))
                """
                self.env.cr.execute(sql_query % (pt.coordinates[0], pt.coordinates[1], pt.coordinates[0], pt.coordinates[1]))
                res = self.env.cr.fetchone()
                self.longitude = res[0]
                self.latitude = res[1]

    geo_point = geo_fields.GeoPoint('Site Location')

    #StandortONr
    number = fields.Char('Site ID', required=True)
    #StandortID
    code = fields.Char('Site ID long', required=True)
    #Standortname
    name = fields.Char('Site name', required=True)

    #MastType
    pole_type = fields.Char('Pole Type')
    #Placement
    placement = fields.Char('Placement')
    #2G_TechSubType
    tech_subtype_2g = fields.Char('2G Tech Subtype')
    #3G_TechSubType
    tech_subtype_3g = fields.Char('3G Tech Subtype')
    #4G_TechSubType
    tech_subtype_4g = fields.Char('4G Tech Subtype')
    #Eigentümer
    owner = fields.Char('Owner')
    #Tragwerkseigentümer
    construction_owner = fields.Char('Construction owner')

    #StandortNutzer_TMA
    site_user_tma = fields.Boolean('StandortNutzer TMA')
    #StandortNutzer_H3A
    site_user_h3a = fields.Boolean('StandortNutzer H3A')
    #ARGE
    arge = fields.Boolean('ARGE')

    #WGS84_Longitude
    longitude = fields.Char('Longitude', required=True)
    #WGS84_Latitude
    latitude = fields.Char('Latitude', required=True)

    #Bezirk
    district = fields.Char('District')
    #PLZ
    postcode = fields.Char('Postcode')
    #Ort
    city = fields.Char('City')
    #Strasse
    street = fields.Char('Street')
    #Housenumber
    house_number = fields.Char('House number')
    #Bundeslandcode
    federal_state_code = fields.Char('Federal state code')
    #Region
    federal_state = fields.Char('Federal state')
    #Telecom
    telecom = fields.Char('Telecom')


