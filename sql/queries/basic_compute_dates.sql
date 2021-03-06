/************************************************************************************************/
/* COMPUTE DATES
 *
 * This query computes the computed_date_start and computed_date_end for
 * all properties of a given type for a given entity and for it's relation.
 *
 *
 * params:
 *    entity_id  :      the id of the entity to postprocess
 *    property_type_id  : the type of property to postprocess
 */
/************************************************************************************************/

SELECT vtm.compute_date_for_property_of_entity(%(entity_id)s,%(property_type_id)s);