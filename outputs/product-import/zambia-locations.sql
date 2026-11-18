-- Add the locations used by the By Nzuri checkout. Run after Django migrations.
-- Existing records are kept. Re-running adds missing entries only.
BEGIN;

INSERT INTO provinces (id, name, slug, sort_order)
VALUES
  (gen_random_uuid(), 'Central', 'central', 0),
  (gen_random_uuid(), 'Copperbelt', 'copperbelt', 1),
  (gen_random_uuid(), 'Eastern', 'eastern', 2),
  (gen_random_uuid(), 'Luapula', 'luapula', 3),
  (gen_random_uuid(), 'Lusaka', 'lusaka', 4),
  (gen_random_uuid(), 'Muchinga', 'muchinga', 5),
  (gen_random_uuid(), 'Northern', 'northern', 6),
  (gen_random_uuid(), 'North-Western', 'north-western', 7),
  (gen_random_uuid(), 'Southern', 'southern', 8),
  (gen_random_uuid(), 'Western', 'western', 9)
ON CONFLICT (slug) DO NOTHING;

WITH seed (province_slug, name, slug) AS (
  VALUES
  ('central', 'Kabwe', 'kabwe'),
  ('central', 'Mkushi', 'mkushi'),
  ('central', 'Mumbwa', 'mumbwa'),
  ('central', 'Serenje', 'serenje'),
  ('central', 'Chibombo', 'chibombo'),
  ('central', 'Kapiri Mposhi', 'kapiri-mposhi'),
  ('copperbelt', 'Kitwe', 'kitwe'),
  ('copperbelt', 'Ndola', 'ndola'),
  ('copperbelt', 'Chingola', 'chingola'),
  ('copperbelt', 'Mufulira', 'mufulira'),
  ('copperbelt', 'Luanshya', 'luanshya'),
  ('copperbelt', 'Kalulushi', 'kalulushi'),
  ('copperbelt', 'Chililabombwe', 'chililabombwe'),
  ('eastern', 'Chipata', 'chipata'),
  ('eastern', 'Petauke', 'petauke'),
  ('eastern', 'Katete', 'katete'),
  ('eastern', 'Lundazi', 'lundazi'),
  ('eastern', 'Nyimba', 'nyimba'),
  ('eastern', 'Sinda', 'sinda'),
  ('luapula', 'Mansa', 'mansa'),
  ('luapula', 'Nchelenge', 'nchelenge'),
  ('luapula', 'Samfya', 'samfya'),
  ('luapula', 'Mwansabombwe', 'mwansabombwe'),
  ('luapula', 'Kawambwa', 'kawambwa'),
  ('lusaka', 'Lusaka', 'lusaka'),
  ('lusaka', 'Chongwe', 'chongwe'),
  ('lusaka', 'Kafue', 'kafue'),
  ('lusaka', 'Rufunsa', 'rufunsa'),
  ('lusaka', 'Luangwa', 'luangwa'),
  ('muchinga', 'Chinsali', 'chinsali'),
  ('muchinga', 'Isoka', 'isoka'),
  ('muchinga', 'Nakonde', 'nakonde'),
  ('muchinga', 'Mpika', 'mpika'),
  ('muchinga', 'Shiwang''andu', 'shiwang''andu'),
  ('northern', 'Kasama', 'kasama'),
  ('northern', 'Mpulungu', 'mpulungu'),
  ('northern', 'Mbala', 'mbala'),
  ('northern', 'Luwingu', 'luwingu'),
  ('northern', 'Mungwi', 'mungwi'),
  ('north-western', 'Solwezi', 'solwezi'),
  ('north-western', 'Mwinilunga', 'mwinilunga'),
  ('north-western', 'Kasempa', 'kasempa'),
  ('north-western', 'Zambezi', 'zambezi'),
  ('north-western', 'Kabompo', 'kabompo'),
  ('southern', 'Livingstone', 'livingstone'),
  ('southern', 'Choma', 'choma'),
  ('southern', 'Monze', 'monze'),
  ('southern', 'Mazabuka', 'mazabuka'),
  ('southern', 'Kalomo', 'kalomo'),
  ('southern', 'Siavonga', 'siavonga'),
  ('western', 'Mongu', 'mongu'),
  ('western', 'Senanga', 'senanga'),
  ('western', 'Sesheke', 'sesheke'),
  ('western', 'Kaoma', 'kaoma'),
  ('western', 'Limulunga', 'limulunga'),
  ('western', 'Lukulu', 'lukulu')
)
INSERT INTO towns (id, province_id, name, slug)
SELECT gen_random_uuid(), p.id, seed.name, seed.slug
FROM seed JOIN provinces p ON p.slug = seed.province_slug
WHERE NOT EXISTS (
  SELECT 1 FROM towns existing
  WHERE existing.province_id = p.id AND lower(existing.name) = lower(seed.name)
)
ON CONFLICT (province_id, slug) DO NOTHING;

COMMIT;

-- Verify the results by province.
SELECT p.name AS province, count(t.id) AS towns
FROM provinces p LEFT JOIN towns t ON t.province_id = p.id
GROUP BY p.id, p.name, p.sort_order
ORDER BY p.sort_order, p.name;
