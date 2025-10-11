INSERT INTO customer (name) VALUES ('University Lab'), ('Factory XYZ');
INSERT INTO experiment_type (name) VALUES ('Impact Test'), ('Load Test');
INSERT INTO measuring_rod (material, geometric_dimensions, physical_properties) VALUES ('Steel', '{"length": 10, "diameter": 2}', '{"density": 7.8, "hardness": 200}'), ('Aluminum', '{"length": 8, "diameter": 1.5}', '{"density": 2.7, "hardness": 150}');
INSERT INTO striker (material, geometric_dimensions) VALUES ('Tungsten', '{"length": 5, "diameter": 1}'), ('Steel', '{"length": 6, "diameter": 1.2}');
INSERT INTO contract (id_customer, date_of_sample_delivery, delivery_type, materials_to_study, technical_specification) VALUES (1, '2025-06-01', 'Local', 'Steel, Aluminum', 'Test impact resistance'), (2, '2025-06-02', 'Ordered', 'Tungsten', 'Test load capacity');
INSERT INTO experiment (experiment_type_code, striker_code, loading_rod_id, support_rod_id, id_contract, experiment_date, comments, media_link, id_result) VALUES (1, 1, 1, 2, 1, '2025-06-03', 'Successful test', '/media/exp1.mp4', 1), (2, 2, 2, 1, 2, '2025-06-04', 'Need review', '/media/exp2.jpg', 2);

INSERT INTO results (physical_measurements, oscillogram_path) 
VALUES ('{"cube_length": 10, "pressure": 100}', '{"points": [[1, 2], [2, 3], [3, 4]]}'), 
('{"radius": 5, "pressure": 150}', '{"points": [[1, 1], [2, 2], [3, 3]]}');

INSERT INTO results (physical_measurements, oscillogram_data) VALUES ('{"cube_length": 10, "pressure": 100}', '{"points": [[4, 4], [5, 5], [6, 6]]}'), ('{"radius": 10, "pressure": 300}', '{"points": [[4, 4], [5, 5], [6, 6]]}');

INSERT INTO experiment (experiment_type_code, striker_code, loading_rod_id, support_rod_id, id_contract, id_material, experiment_date, comments, media_link, id_result) 
VALUES (1, 1, 1, 2, 1, 1, '2025-06-03', 'Successful test', '/media/exp1.mp4', 1);