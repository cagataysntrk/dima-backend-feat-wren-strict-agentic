CREATE TABLE IF NOT EXISTS orders (
    id          integer PRIMARY KEY,
    order_date  date NOT NULL,
    region      text NOT NULL,
    channel     text NOT NULL,
    amount      numeric(12,2) NOT NULL
);

INSERT INTO orders (id, order_date, region, channel, amount)
SELECT
    i,
    DATE '2026-01-01' + ((i - 1) % 240),
    (ARRAY['North','South','East','West'])[((i - 1) % 4) + 1],
    (ARRAY['Web','Store','Partner'])[((i - 1) % 3) + 1],
    (100 + (i * 7 % 900))::numeric(12,2)
FROM generate_series(1, 250) AS g(i)
ON CONFLICT (id) DO NOTHING;

CREATE INDEX IF NOT EXISTS orders_order_date_idx ON orders(order_date);
CREATE INDEX IF NOT EXISTS orders_region_idx ON orders(region);
