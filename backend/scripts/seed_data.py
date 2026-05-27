import os
import sys
import uuid
import numpy as np
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import bcrypt

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import AsyncSessionLocal, engine
from app.models import Base
from app.models.users import User
from app.models.customers import Customer
from app.models.transactions import Transaction
from app.models.segments import Segment

# Set random seed for reproducibility
np.random.seed(42)

async def seed_all():
    print("Starting database seeding...")
    
    # 1. Initialize Tables (clean restart)
    async with engine.begin() as conn:
        print("Recreating database tables...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    db = AsyncSessionLocal()
    
    try:
        # 2. Seed Admin User
        print("Seeding admin user...")
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@customeriq.com",
            hashed_password=bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        await db.commit()
        print("Admin user seeded successfully!")
        
        # 3. Create initial segments placeholders
        print("Creating segments...")
        segment_data = [
            ("Premium Loyalists", "premium-loyalists", "High-income, high-spend customers purchasing frequently.", "#3B82F6", "award"),
            ("Growth Potential", "growth-potential", "Frequent shoppers with moderate order values.", "#10B981", "trending-up"),
            ("Dormant Champions", "dormant-champions", "Previously high-value customers who haven't purchased in a while.", "#F59E0B", "clock"),
            ("New Explorers", "new-explorers", "Recent customers with low overall spend.", "#EF4444", "users"),
            ("At-Risk Churners", "at-risk-churners", "Customers showing strong indicators of churning.", "#8B5CF6", "alert-triangle"),
            ("Bargain Hunters", "bargain-hunters", "Price-sensitive buyers with average engagement.", "#EC4899", "shopping-bag")
        ]
        
        segments = []
        for name, slug, desc, color, icon in segment_data:
            seg = Segment(
                name=name,
                slug=slug,
                description=desc,
                color_hex=color,
                icon=icon,
                avg_clv=Decimal("0"),
                avg_order_value=Decimal("0"),
                churn_rate=Decimal("0.10"),
                size=0,
                revenue_share=Decimal("0"),
                marketing_strategy="",
                priority_score=5
            )
            db.add(seg)
            segments.append(seg)
            
        await db.commit()
        print("Segments seeded.")
        
        # 4. Generate 10,000 Customers
        print("Generating 10,000 customers (realistic distributions)...")
        num_customers = 10000
        
        # Distributions
        ages = np.clip(np.random.normal(34, 11, num_customers).astype(int), 18, 70)
        
        # Income log-normal
        incomes = np.random.lognormal(mean=10.8, sigma=0.6, size=num_customers)
        # Scale to range approx 25k - 25L INR
        incomes = np.clip(incomes * 15, 25000, 2500000)
        
        # Total Spend: correlated with income + noise
        spend_corr = incomes * 0.4 + np.random.normal(0, incomes * 0.1, num_customers)
        total_spends = np.clip(spend_corr, 500, incomes * 0.9)
        
        # Purchase Frequency (Poisson lambda=8 per year, so ~16 over 2 years)
        purchase_freqs = np.clip(np.random.poisson(8, num_customers), 1, 100)
        
        # Avg Order Value = Total Spend / Purchase Frequency
        avg_ovs = total_spends / purchase_freqs
        
        # Recency (Days since last purchase, exponential distribution)
        recency_days = np.clip(np.random.exponential(45, num_customers).astype(int), 0, 730)
        
        # Demographics
        genders = np.random.choice(["Male", "Female", "Other"], size=num_customers, p=[0.52, 0.46, 0.02])
        regions = np.random.choice(
            ["Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Telangana", "Gujarat", "Other"],
            size=num_customers,
            p=[0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.17]
        )
        categories = np.random.choice(
            ["Electronics", "Fashion", "Groceries", "Beauty", "Sports", "Others"],
            size=num_customers,
            p=[0.22, 0.28, 0.20, 0.15, 0.10, 0.05]
        )
        membership_statuses = np.random.choice(
            ["standard", "premium", "gold", "platinum"],
            size=num_customers,
            p=[0.60, 0.25, 0.12, 0.03]
        )
        
        # Behavior / Engagement
        cart_abandonment_rates = np.random.beta(2, 5, num_customers) # skewed lower
        return_rates = np.random.beta(1, 10, num_customers) # skewed very low
        email_open_rates = np.random.beta(3, 7, num_customers) # mean ~30%
        app_usage_scores = np.random.normal(60, 15, num_customers)
        app_usage_scores = np.clip(app_usage_scores, 0, 100)
        loyalty_points_arr = (total_spends * 0.05).astype(int)
        referral_counts = np.random.poisson(1, num_customers)
        
        # Introduce 4% MCAR missing values across some numeric columns
        for col in [ages, incomes, cart_abandonment_rates, return_rates, email_open_rates, app_usage_scores]:
            mask = np.random.random(num_customers) < 0.04
            # We will handle converting this in Python
            
        print("Instantiating Customer objects...")
        customers_list = []
        customer_ids = []
        
        # Precompute normalization bounds for RFM & Engagement
        rec_min, rec_max = recency_days.min(), recency_days.max()
        freq_min, freq_max = purchase_freqs.min(), purchase_freqs.max()
        spend_min, spend_max = total_spends.min(), total_spends.max()
        
        email_min, email_max = email_open_rates.min(), email_open_rates.max()
        app_min, app_max = app_usage_scores.min(), app_usage_scores.max()
        loy_min, loy_max = loyalty_points_arr.min(), loyalty_points_arr.max()
        
        for i in range(num_customers):
            c_id = uuid.uuid4()
            customer_ids.append(c_id)
            
            # Recency normalized (lower is better, so 1 - normalized)
            r_norm = 1.0 - (recency_days[i] - rec_min) / (rec_max - rec_min) if rec_max > rec_min else 1.0
            f_norm = (purchase_freqs[i] - freq_min) / (freq_max - freq_min) if freq_max > freq_min else 1.0
            m_norm = (total_spends[i] - spend_min) / (spend_max - spend_min) if spend_max > spend_min else 1.0
            
            # Scores
            rfm = 0.4 * r_norm + 0.35 * f_norm + 0.25 * m_norm
            
            # Engagement
            email_n = (email_open_rates[i] - email_min) / (email_max - email_min) if email_max > email_min else 1.0
            app_n = (app_usage_scores[i] - app_min) / (app_max - app_min) if app_max > app_min else 1.0
            loy_n = (loyalty_points_arr[i] - loy_min) / (loy_max - loy_min) if loy_max > loy_min else 1.0
            
            engagement = 0.3 * email_n + 0.4 * app_n + 0.3 * loy_n
            clv = avg_ovs[i] * purchase_freqs[i] * 2.5
            
            # Create Customer model
            customer = Customer(
                id=c_id,
                external_id=f"IQ-{i+10001}",
                age=int(ages[i]) if np.random.random() > 0.04 else None,
                gender=genders[i],
                region=regions[i],
                country="India",
                membership_status=membership_statuses[i],
                annual_income=Decimal(f"{incomes[i]:.2f}") if np.random.random() > 0.04 else None,
                total_spend=Decimal(f"{total_spends[i]:.2f}"),
                avg_order_value=Decimal(f"{avg_ovs[i]:.2f}"),
                clv_estimate=Decimal(f"{clv:.2f}"),
                purchase_frequency=int(purchase_freqs[i]),
                days_since_last_purchase=int(recency_days[i]),
                cart_abandonment_rate=Decimal(f"{cart_abandonment_rates[i]:.4f}") if np.random.random() > 0.04 else None,
                return_rate=Decimal(f"{return_rates[i]:.4f}") if np.random.random() > 0.04 else None,
                email_open_rate=Decimal(f"{email_open_rates[i]:.4f}") if np.random.random() > 0.04 else None,
                app_usage_score=Decimal(f"{app_usage_scores[i]:.2f}") if np.random.random() > 0.04 else None,
                loyalty_points=int(loyalty_points_arr[i]),
                referral_count=int(referral_counts[i]),
                rfm_score=Decimal(f"{rfm*10:.2f}"),
                engagement_index=Decimal(f"{engagement*10:.2f}"),
                churn_probability=Decimal("0.15"),
                value_tier="premium" if total_spends[i] > 100000 else "standard",
                predicted_clv_90d=Decimal("0"),
                preferred_category=categories[i],
                created_at=datetime.now() - timedelta(days=int(np.random.randint(60, 730)))
            )
            customers_list.append(customer)
            
        print("Bulk inserting customers...")
        # Split into chunks of 1000 for efficient commit
        for chunk in range(0, num_customers, 1000):
            db.add_all(customers_list[chunk:chunk+1000])
            await db.commit()
            print(f"Inserted customers {chunk} to {chunk+1000}")
            
        # 5. Generate 80,000 Transactions
        print("Generating 80,000 transactions over 24 months...")
        num_transactions = 80000
        transactions_list = []
        
        # Match order counts to customer frequency requirements
        # Create transaction array
        # Precompute random customer choices and dates
        random_customers = np.random.choice(customer_ids, size=num_transactions)
        
        # Seasonality distribution weights: higher in Oct-Nov (Diwali), Dec-Jan (New Year)
        months_pool = []
        for m in range(24):
            date = datetime.now() - timedelta(days=m*30)
            month_num = date.month
            weight = 1
            if month_num in [10, 11]: # Diwali season
                weight = 3
            elif month_num in [12, 1]: # Winter/New Year
                weight = 2
            for _ in range(weight):
                months_pool.append(date)
                
        random_months = np.random.choice(months_pool, size=num_transactions)
        
        # Transaction amount bases per category
        category_bases = {
            "Electronics": 15000,
            "Fashion": 2500,
            "Groceries": 1500,
            "Beauty": 1800,
            "Sports": 3500,
            "Others": 1200
        }
        categories_list = list(category_bases.keys())
        random_categories = np.random.choice(categories_list, size=num_transactions, p=[0.22, 0.28, 0.20, 0.15, 0.10, 0.05])
        
        random_channels = np.random.choice(["Web", "Mobile App", "Physical Store"], size=num_transactions, p=[0.40, 0.45, 0.15])
        random_discounts = np.random.choice([0, 0.05, 0.10, 0.15, 0.20], size=num_transactions, p=[0.60, 0.15, 0.12, 0.08, 0.05])
        random_items_count = np.random.choice([1, 2, 3, 4, 5], size=num_transactions, p=[0.50, 0.25, 0.13, 0.08, 0.04])
        random_statuses = np.random.choice(["completed", "returned", "failed"], size=num_transactions, p=[0.92, 0.06, 0.02])
        
        for i in range(num_transactions):
            cat = random_categories[i]
            base_amt = category_bases[cat]
            # Add normal distribution noise
            amount = np.clip(np.random.normal(base_amt, base_amt*0.2), base_amt*0.5, base_amt*2.0)
            
            # Apply discount
            discount = random_discounts[i]
            amount = amount * (1.0 - discount)
            
            # Deduct random days within that month
            tx_date = random_months[i] - timedelta(days=int(np.random.randint(0, 30)))
            
            tx = Transaction(
                id=uuid.uuid4(),
                customer_id=random_customers[i],
                order_id=f"ORD-{i+100001}",
                transaction_date=tx_date,
                amount=Decimal(f"{amount:.2f}"),
                category=cat,
                items_count=int(random_items_count[i]),
                status=random_statuses[i],
                channel=random_channels[i],
                discount_applied=Decimal(f"{discount:.4f}"),
                created_at=tx_date
            )
            transactions_list.append(tx)
            
        print("Bulk inserting transactions...")
        for chunk in range(0, num_transactions, 2000):
            db.add_all(transactions_list[chunk:chunk+2000])
            await db.commit()
            print(f"Inserted transactions {chunk} to {chunk+2000}")
            
        print("Database seeded completely and successfully!")
        
    except Exception as e:
        await db.rollback()
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_all())
