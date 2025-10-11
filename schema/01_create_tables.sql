CREATE TABLE customer (
    id_customer SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE contract (
    id_contract SERIAL PRIMARY KEY,
    id_customer INT NOT NULL,
    date_of_sample_delivery DATE NOT NULL,
    technical_specification TEXT,
    delivery_type VARCHAR(50) NOT NULL,
    materials_to_study TEXT NOT NULL,
    report TEXT,
    contract_document TEXT,
    FOREIGN KEY (id_customer) 
	REFERENCES customer(id_customer) ON DELETE RESTRICT
);

CREATE TABLE experiment_type (
    experiment_type_code SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE materials (
    id_material SERIAL PRIMARY KEY,
    name_of_material VARCHAR(255) NOT NULL
);

CREATE TABLE striker (
    striker_code SERIAL PRIMARY KEY,
    material VARCHAR(255) NOT NULL,
    geometric_dimensions JSONB NOT NULL
);

CREATE TABLE measuring_rod (
    id_rod SERIAL PRIMARY KEY,
    material VARCHAR(255) NOT NULL,
    geometric_dimensions JSONB NOT NULL,
    physical_properties JSONB NOT NULL
);

CREATE TABLE results (
    id_result SERIAL PRIMARY KEY,
    physical_measurements JSONB NOT NULL,
    oscillogram_path TEXT
);

CREATE TABLE experiment (
    id_experiment SERIAL PRIMARY KEY,
    experiment_type_code INT NOT NULL,
    striker_code INT NOT NULL,
    loading_rod_id INT NOT NULL,
    support_rod_id INT NOT NULL,
    id_contract INT NOT NULL,
    id_material INT NOT NULL,
    experiment_date DATE NOT NULL,
    comments TEXT,
    media_link TEXT,
    id_result INT NOT NULL,
    CONSTRAINT unique_result UNIQUE (id_result),
    FOREIGN KEY (experiment_type_code) REFERENCES experiment_type(experiment_type_code) ON DELETE RESTRICT,
    FOREIGN KEY (striker_code) REFERENCES striker(striker_code) ON DELETE RESTRICT,
    FOREIGN KEY (loading_rod_id) REFERENCES measuring_rod(id_rod) ON DELETE RESTRICT,
    FOREIGN KEY (support_rod_id) REFERENCES measuring_rod(id_rod) ON DELETE RESTRICT,
    FOREIGN KEY (id_contract) REFERENCES contract(id_contract) ON DELETE RESTRICT,
    FOREIGN KEY (id_material) REFERENCES materials(id_material) ON DELETE RESTRICT,
    FOREIGN KEY (id_result) REFERENCES results(id_result) ON DELETE CASCADE
);