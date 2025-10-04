#!/usr/bin/env python3
"""Update user language preferences"""

from src.utils.clickhouse_client import db_client

# Update Maria to prefer Spanish (family in Brazil speaks Portuguese/Spanish)
db_client.client.command("""
    ALTER TABLE users 
    UPDATE preferences = JSONExtractString(preferences, 'preferred_language', 'es')
    WHERE user_id = 'demo_maria'
""")

# Update Kwame to prefer French (common in Kenya/Rwanda)
db_client.client.command("""
    ALTER TABLE users
    UPDATE preferences = JSONExtractString(preferences, 'preferred_language', 'fr')
    WHERE user_id = 'demo_kwame'
""")

print("✅ Updated user language preferences")
print("- Maria Silva: Spanish (es)")
print("- Kwame Osei: French (fr)")
