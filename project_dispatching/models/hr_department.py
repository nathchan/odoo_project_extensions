from openerp import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    @api.multi
    def _compute_name(self):
        for rec in self:
            count = self.env['hr.employee'].search([('department_id', '=', rec.id)], count=True)
            rec.compute_name = rec.name + ' (' + str(count) + ')'

    compute_name = fields.Char('Name', compute=_compute_name)

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        name = 'compute_name'
        if name in self._fields:
            convert = self._fields[name].convert_to_display_name
            for record in self:
                result.append((record.id, convert(record[name], record)))
        else:
            for record in self:
                result.append((record.id, "%s,%s" % (record._name, record.id)))

        return result
