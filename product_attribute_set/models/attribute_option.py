##############################################################################
# Copyright (c) 2022 brain-tec AG (https://bt-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import fields, models


class AttributeOption(models.Model):
    _inherit = "attribute.option"

    linked_attribute_option_id = fields.Many2one(
        'attribute.option', readonly=True, copy=False)

    def copy_to_model(self):
        """Returns a new record with the same fields in the new model"""
        self.ensure_one()
        if self.attribute_id.linked_attribute_attribute_id:
            new_attribute_option = self.copy({
                'attribute_id': self.attribute_id.linked_attribute_attribute_id.id,
            })
            self.write({
                'linked_attribute_option_id': new_attribute_option.id,
            })
            return new_attribute_option
        return None

    def write(self, vals):
        """Updates the linked groups if the record updated has any"""
        ret = super().write(vals)
        linked_options = self.mapped('linked_attribute_option_id')
        if linked_options:
            if 'linked_attribute_option_id' in vals:
                del vals['linked_attribute_option_id']
            if vals:
                linked_options.write(vals)
        return ret

    def unlink(self):
        """Deletes the linked groups if the record updated has any"""
        linked_options = self.mapped('linked_attribute_option_id')
        if linked_options:
            linked_options.unlink()
        return super().unlink()
