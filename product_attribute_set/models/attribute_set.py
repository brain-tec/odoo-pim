##############################################################################
# Copyright (c) 2022 brain-tec AG (https://bt-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class AttributeSet(models.Model):
    _inherit = "attribute.set"

    linked_attribute_set_id = fields.Many2one(
        'attribute.set', readonly=True, copy=False)

    def copy_to_model(self, new_model_id):
        """Returns a new record with the same fields in the new model"""
        self.ensure_one()
        new_attribute_set = self.copy({
            'attribute_ids': [
                (6, 0,
                 self.attribute_ids.mapped('linked_attribute_attribute_id.id')),
            ],
            'model_id': new_model_id,
        })
        self.write({
            'linked_attribute_set_id': new_attribute_set.id,
        })
        return new_attribute_set

    @api.model
    def create(self, vals):
        """Creates a new field in product.product if we create it for
        product.template"""
        attribute_set = super().create(vals)
        if attribute_set.model_id.model == 'product.template':
            attribute_set.copy_to_model(
                self.env.ref("product.model_product_product").id)
        return attribute_set

    def write(self, vals):
        """Updates the linked sets if the record updated has any"""
        ret = super().write(vals)
        linked_sets = self.mapped('linked_attribute_set_id')
        if linked_sets:
            if 'linked_attribute_set_id' in vals:
                del vals['linked_attribute_set_id']
            if vals:
                linked_sets.write(vals)
        return ret

    def unlink(self):
        """Deletes the linked sets if the record updated has any"""
        linked_sets = self.mapped('linked_attribute_set_id')
        if linked_sets:
            linked_sets.unlink()
        return super().unlink()
