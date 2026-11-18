-- Review prices, descriptions and availability before running.
-- Adds missing methods without changing existing methods. Run after Django migrations.
BEGIN;
WITH seed (name, description, price, estimated_days, sort_order) AS (
  VALUES
    ('Lusaka Delivery', 'Same-day and next-day delivery within Lusaka', 35.00::numeric, '1-2 days', 1),
    ('Intercity Courier', 'Courier delivery to major towns across Zambia', 65.00::numeric, '2-5 days', 2),
    ('Bus Freight', 'Economy bus freight to all provinces', 45.00::numeric, '3-7 days', 3),
    ('Store Pickup', 'Pick up from our Lusaka showroom', 0.00::numeric, 'Same day', 4)
)
INSERT INTO delivery_methods (id, name, description, price, estimated_days, is_active, sort_order)
SELECT gen_random_uuid(), s.name, s.description, s.price, s.estimated_days, true, s.sort_order
FROM seed s
WHERE NOT EXISTS (SELECT 1 FROM delivery_methods d WHERE lower(d.name) = lower(s.name));
COMMIT;

SELECT name, price, estimated_days, is_active FROM delivery_methods ORDER BY sort_order, name;
