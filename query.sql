SELECT
    (SUM(CASE WHEN OrderType.name = 'Contrassegno' THEN Order.price * Order.quantity ELSE 0 END) / SUM(Order.price * Order.quantity)) * 100 AS PercentualeContrassegno,
    (SUM(CASE WHEN OrderType.name = 'Online' THEN Order.price * Order.quantity ELSE 0 END) / SUM(Order.price * Order.quantity)) * 100 AS PercentualeOnline
FROM Order, OrderType
WHERE Order.type_id = OrderType.id;
