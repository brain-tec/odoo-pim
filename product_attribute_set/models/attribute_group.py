##############################################################################
# Copyright (c) 2022 brain-tec AG (https://bt-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class AttributeGroup(models.Model):
    _inherit = "attribute.group"

    linked_attribute_group_id = fields.Many2one(
        'attribute.group', readonly=True, copy=False)

    def copy_to_model(self, new_model_id):
        """Returns a new record with the same fields in the new model"""
        self.ensure_one()
        new_attribute_group = self.copy({
            'model_id': new_model_id,
        })
        self.write({
            'linked_attribute_group_id': new_attribute_group.id,
        })
        return new_attribute_group

    @api.model
    def create(self, vals):
        """Creates a new field in product.product if we create it for
        product.template"""
        attribute_group = super().create(vals)
        if attribute_group.model_id.model == 'product.template':
            attribute_group.copy_to_model(
                self.env.ref("product.model_product_product").id)
        return attribute_group

    def write(self, vals):
        """Updates the linked groups if the record updated has any"""
        ret = super().write(vals)
        linked_groups = self.mapped('linked_attribute_group_id')
        if linked_groups:
            if 'linked_attribute_group_id' in vals:
                del vals['linked_attribute_group_id']
            if vals:
                linked_groups.write(vals)
        return ret

    def unlink(self):
        """Deletes the linked groups if the record updated has any"""
        linked_groups = self.mapped('linked_attribute_group_id')
        if linked_groups:
            linked_groups.unlink()
        return super().unlink()
