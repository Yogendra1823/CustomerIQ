CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE users (
	id CHAR(32) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	full_name VARCHAR(200), 
	role VARCHAR(20), 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE segments (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	slug VARCHAR(100) NOT NULL, 
	description TEXT, 
	color_hex VARCHAR(7), 
	icon VARCHAR(50), 
	avg_clv NUMERIC(12, 2), 
	avg_order_value NUMERIC(10, 2), 
	churn_rate NUMERIC(5, 4), 
	size INTEGER, 
	revenue_share NUMERIC(5, 4), 
	marketing_strategy TEXT, 
	priority_score INTEGER, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	UNIQUE (slug)
);

CREATE TABLE ml_runs (
	id CHAR(32) NOT NULL, 
	run_name VARCHAR(200), 
	algorithm VARCHAR(50), 
	n_clusters INTEGER, 
	silhouette_score NUMERIC(6, 4), 
	davies_bouldin_score NUMERIC(6, 4), 
	inertia NUMERIC(12, 2), 
	training_samples INTEGER, 
	feature_count INTEGER, 
	runtime_seconds NUMERIC(6, 2), 
	model_path VARCHAR(500), 
	parameters JSON, 
	metrics JSON, 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
);

CREATE TABLE customers (
	id CHAR(32) NOT NULL, 
	external_id VARCHAR(100) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME, 
	age INTEGER, 
	gender VARCHAR(20), 
	region VARCHAR(100), 
	country VARCHAR(100), 
	membership_status VARCHAR(20), 
	annual_income NUMERIC(12, 2), 
	total_spend NUMERIC(12, 2), 
	avg_order_value NUMERIC(10, 2), 
	clv_estimate NUMERIC(12, 2), 
	purchase_frequency INTEGER, 
	days_since_last_purchase INTEGER, 
	cart_abandonment_rate NUMERIC(5, 4), 
	return_rate NUMERIC(5, 4), 
	email_open_rate NUMERIC(5, 4), 
	app_usage_score NUMERIC(5, 2), 
	loyalty_points INTEGER, 
	referral_count INTEGER, 
	rfm_score NUMERIC(5, 2), 
	engagement_index NUMERIC(5, 2), 
	churn_probability NUMERIC(5, 4), 
	value_tier VARCHAR(20), 
	predicted_clv_90d NUMERIC(12, 2), 
	preferred_category VARCHAR(100), 
	segment_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (external_id), 
	FOREIGN KEY(segment_id) REFERENCES segments (id)
);

CREATE TABLE transactions (
	id CHAR(32) NOT NULL, 
	customer_id CHAR(32), 
	order_id VARCHAR(100) NOT NULL, 
	transaction_date DATETIME NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	category VARCHAR(100), 
	items_count INTEGER, 
	status VARCHAR(20), 
	channel VARCHAR(50), 
	discount_applied NUMERIC(5, 4), 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE CASCADE, 
	UNIQUE (order_id)
);

