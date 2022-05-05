##############################################################################
# Copyright (c) 2022 brain-tec AG (https://bt-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, fields, models


class AttributeAttribute(models.Model):
    _inherit = "attribute.attribute"

    linked_attribute_attribute_id = fields.Many2one(
        'attribute.attribute', readonly=True, copy=False)

    def copy_to_model(self, new_model_id):
        """Returns a new record with the same fields and group in the new model"""
        self.ensure_one()
        if self.nature == 'custom' and self.model_id.model == 'product.template':
            if self.attribute_group_id:
                if self.attribute_group_id.linked_attribute_group_id:
                    attribute_group_id = \
                        self.attribute_group_id.linked_attribute_group_id.id
                else:
                    attribute_group_id = \
                        self.attribute_group_id.copy_to_model(new_model_id).id
            else:
                attribute_group_id = None
            new_field = self.env['ir.model.fields'].search(
                [('model_id', '=', new_model_id),
                 ('name', '=', self.field_id.name)],
                limit=1,
            )
            if new_field:
                new_attribute = self.create({
                    'nature': 'native',
                    'model_id': new_model_id,
                    'field_id': new_field.id,
                    'attribute_group_id': attribute_group_id,
                    'sequence': self.sequence,
                    'required_on_views': self.required_on_views,
                    'attribute_set_ids': [
                        (6, 0,
                         self.attribute_set_ids.mapped(
                             'linked_attribute_set_id.id')),
                    ],
                    'option_ids': None,
                    'attribute_type': self.attribute_type,
                    'serialized': self.serialized,
                })
                self.env.cr.execute(
                    "UPDATE ir_model_fields "
                    "SET state='manual', related=null, compute=null "
                    "WHERE id = %s",
                    (new_attribute.field_id.id, )
                )
                new_attribute.invalidate_cache()
                new_attribute.write({
                    'nature': 'custom',
                    'store': True,
                })
                self.write({
                    'linked_attribute_attribute_id': new_attribute.id,
                })
                for option in self.option_ids:
                    option.copy_to_model()
                return new_attribute

        return None

    @api.model
    def create(self, vals):
        """Creates a new field in product.product if we create it for
        product.template"""
        attribute_attribute = super(
            AttributeAttribute, self.with_context(ge_pim=True)).create(vals)
        if attribute_attribute.model_id.model == 'product.template':
            attribute_attribute.copy_to_model(
                self.env.ref("product.model_product_product").id)
        return attribute_attribute

    def write(self, vals):
        """Updates the linked attributes if the record updated has any"""
        ret = super().write(vals)
        linked_attributes = self.mapped('linked_attribute_attribute_id')
        if linked_attributes:
            if 'linked_attribute_attribute_id' in vals:
                del vals['linked_attribute_attribute_id']
            if 'attribute_set_ids' in vals:
                self.ensure_one()  # for simplicity, otherwise refactor
                vals['attribute_set_ids'] = [
                    (6, 0,
                     self.attribute_set_ids.mapped('linked_attribute_set_id.id')),
                ]
            if 'option_ids' in vals:
                del vals['option_ids']
                self.ensure_one()  # for simplicity, otherwise refactor
                for option in self.option_ids:
                    if not option.linked_attribute_option_id:
                        option.copy_to_model()
            if vals:
                linked_attributes.write(vals)
        return ret

    def unlink(self):
        """Deletes the linked attributes if the record updated has any"""
        linked_attributes = self.mapped('linked_attribute_attribute_id')
        if linked_attributes:
            linked_attributes.unlink()
        return super().unlink()
