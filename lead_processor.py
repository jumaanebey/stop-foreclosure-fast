import pandas as pd
import requests
import json
import time
from datetime import datetime
import os
from typing import Dict, List, Optional
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeadProcessor:
    def __init__(self):
        # API Configuration
        self.config = {
            # Lead Enrichment APIs
            'hunter_api_key': os.getenv('HUNTER_API_KEY', 'YOUR_HUNTER_API_KEY'),
            'apollo_api_key': os.getenv('APOLLO_API_KEY', 'YOUR_APOLLO_API_KEY'),
            
            # Marketing Platform APIs
            'mailchimp_api_key': os.getenv('MAILCHIMP_API_KEY', 'YOUR_MAILCHIMP_API_KEY'),
            'mailchimp_server': os.getenv('MAILCHIMP_SERVER', 'us1'),  # e.g., us1, us2, etc.
            'mailchimp_list_id': os.getenv('MAILCHIMP_LIST_ID', 'YOUR_LIST_ID'),
            
            'twilio_account_sid': os.getenv('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_SID'),
            'twilio_auth_token': os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_TOKEN'),
            'twilio_phone_number': os.getenv('TWILIO_PHONE', '+1234567890'),
            
            # Google Ads
            'google_ads_customer_id': os.getenv('GOOGLE_ADS_CUSTOMER_ID', 'YOUR_CUSTOMER_ID'),
            'google_ads_developer_token': os.getenv('GOOGLE_ADS_DEV_TOKEN', 'YOUR_DEV_TOKEN'),
            'google_ads_client_id': os.getenv('GOOGLE_ADS_CLIENT_ID', 'YOUR_CLIENT_ID'),
            'google_ads_client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET', 'YOUR_CLIENT_SECRET'),
            'google_ads_refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN', 'YOUR_REFRESH_TOKEN'),
            
            # Facebook Ads
            'facebook_access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', 'YOUR_FB_ACCESS_TOKEN'),
            'facebook_ad_account_id': os.getenv('FACEBOOK_AD_ACCOUNT_ID', 'act_YOUR_AD_ACCOUNT_ID'),
            'facebook_app_id': os.getenv('FACEBOOK_APP_ID', 'YOUR_APP_ID'),
            'facebook_app_secret': os.getenv('FACEBOOK_APP_SECRET', 'YOUR_APP_SECRET'),
        }
        
        self.processed_leads = []
        self.enriched_leads = []
        
    def load_retran_data(self, file_path: str) -> pd.DataFrame:
        """Load and parse Retran.com CSV/XLS data"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or XLS/XLSX")
            
            logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            raise
    
    def clean_and_standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the lead data"""
        # Expected Retran.com format columns (adjust as needed)
        column_mapping = {
            'property_address': ['address', 'property_address', 'street_address', 'full_address'],
            'owner_name': ['name', 'owner_name', 'property_owner', 'full_name'],
            'phone': ['phone', 'phone_number', 'contact_phone', 'primary_phone'],
            'city': ['city', 'property_city'],
            'state': ['state', 'property_state'],
            'zip': ['zip', 'zipcode', 'postal_code', 'zip_code'],
            'foreclosure_date': ['foreclosure_date', 'sale_date', 'auction_date'],
            'loan_amount': ['loan_amount', 'debt_amount', 'principal_balance']
        }
        
        # Standardize column names
        standardized_df = pd.DataFrame()
        for standard_col, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col.lower() in [c.lower() for c in df.columns]:
                    actual_col = next(c for c in df.columns if c.lower() == col.lower())
                    standardized_df[standard_col] = df[actual_col]
                    break
        
        # Clean the data
        logger.info("Cleaning and standardizing data...")
        
        # Remove duplicates based on address + name
        standardized_df['duplicate_key'] = (
            standardized_df['property_address'].astype(str).str.lower() + 
            standardized_df['owner_name'].astype(str).str.lower()
        )
        standardized_df = standardized_df.drop_duplicates(subset=['duplicate_key'])
        standardized_df = standardized_df.drop('duplicate_key', axis=1)
        
        # Clean phone numbers
        if 'phone' in standardized_df.columns:
            standardized_df['phone'] = standardized_df['phone'].astype(str).str.replace(r'[^\d]', '', regex=True)
            standardized_df['phone'] = standardized_df['phone'].apply(
                lambda x: f"+1{x}" if len(x) == 10 else x if len(x) == 11 else None
            )
        
        # Remove records with missing critical data
        critical_columns = ['property_address', 'owner_name']
        for col in critical_columns:
            if col in standardized_df.columns:
                standardized_df = standardized_df.dropna(subset=[col])
        
        # Add processed timestamp
        standardized_df['processed_date'] = datetime.now().isoformat()
        
        logger.info(f"Cleaned data: {len(standardized_df)} records remaining")
        return standardized_df
    
    def enrich_with_hunter(self, email_domain: str) -> Optional[str]:
        """Enrich lead with email using Hunter.io API"""
        if not self.config['hunter_api_key'] or self.config['hunter_api_key'] == 'YOUR_HUNTER_API_KEY':
            return None
            
        url = f"https://api.hunter.io/v2/domain-search"
        params = {
            'domain': email_domain,
            'api_key': self.config['hunter_api_key'],
            'limit': 1
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('emails'):
                    return data['data']['emails'][0]['value']
        except Exception as e:
            logger.error(f"Hunter.io API error: {str(e)}")
        
        return None
    
    def enrich_with_apollo(self, name: str, company: str = None) -> Dict:
        """Enrich lead with Apollo.io API"""
        if not self.config['apollo_api_key'] or self.config['apollo_api_key'] == 'YOUR_APOLLO_API_KEY':
            return {}
            
        url = "https://api.apollo.io/v1/mixed_people/search"
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': self.config['apollo_api_key']
        }
        
        data = {
            'q_keywords': name,
            'page': 1,
            'per_page': 1
        }
        
        if company:
            data['q_organization_domains'] = company
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('people'):
                    person = result['people'][0]
                    return {
                        'email': person.get('email'),
                        'linkedin_url': person.get('linkedin_url'),
                        'title': person.get('title'),
                        'organization': person.get('organization', {}).get('name')
                    }
        except Exception as e:
            logger.error(f"Apollo.io API error: {str(e)}")
        
        return {}
    
    def enrich_leads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich leads with email and additional data"""
        logger.info("Starting lead enrichment...")
        enriched_df = df.copy()
        
        # Add email column if not exists
        if 'email' not in enriched_df.columns:
            enriched_df['email'] = None
        
        for index, row in enriched_df.iterrows():
            # Skip if email already exists
            if pd.notna(row.get('email')):
                continue
                
            name = row.get('owner_name', '')
            
            # Try to extract domain from address for Hunter.io
            if 'property_address' in row:
                address_parts = str(row['property_address']).split()
                potential_domains = [part for part in address_parts if '.' in part]
                
                for domain in potential_domains:
                    email = self.enrich_with_hunter(domain)
                    if email:
                        enriched_df.at[index, 'email'] = email
                        break
            
            # Try Apollo.io for professional email
            if pd.isna(enriched_df.at[index, 'email']):
                apollo_data = self.enrich_with_apollo(name)
                if apollo_data.get('email'):
                    enriched_df.at[index, 'email'] = apollo_data['email']
                    enriched_df.at[index, 'linkedin_url'] = apollo_data.get('linkedin_url')
                    enriched_df.at[index, 'job_title'] = apollo_data.get('title')
            
            # Rate limiting
            time.sleep(0.5)
        
        logger.info(f"Enrichment complete. Found emails for {enriched_df['email'].notna().sum()} leads")
        return enriched_df
    
    def sync_to_mailchimp(self, df: pd.DataFrame) -> bool:
        """Sync leads to Mailchimp email list"""
        if not self.config['mailchimp_api_key'] or self.config['mailchimp_api_key'] == 'YOUR_MAILCHIMP_API_KEY':
            logger.warning("Mailchimp API key not configured")
            return False
            
        url = f"https://{self.config['mailchimp_server']}.api.mailchimp.com/3.0/lists/{self.config['mailchimp_list_id']}/members"
        headers = {
            'Authorization': f"Bearer {self.config['mailchimp_api_key']}",
            'Content-Type': 'application/json'
        }
        
        success_count = 0
        for _, row in df.iterrows():
            if pd.isna(row.get('email')):
                continue
                
            member_data = {
                'email_address': row['email'],
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': row.get('owner_name', '').split()[0] if row.get('owner_name') else '',
                    'LNAME': ' '.join(row.get('owner_name', '').split()[1:]) if row.get('owner_name') else '',
                    'PHONE': row.get('phone', ''),
                    'ADDRESS': row.get('property_address', ''),
                    'CITY': row.get('city', ''),
                    'STATE': row.get('state', ''),
                    'ZIP': row.get('zip', '')
                },
                'tags': ['foreclosure-lead', 'retran-import']
            }
            
            try:
                response = requests.post(url, headers=headers, json=member_data)
                if response.status_code in [200, 201]:
                    success_count += 1
                elif response.status_code == 400:
                    # Member already exists, update instead
                    member_hash = hashlib.md5(row['email'].lower().encode()).hexdigest()
                    update_url = f"{url}/{member_hash}"
                    requests.put(update_url, headers=headers, json=member_data)
                    success_count += 1
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Mailchimp sync error for {row.get('email')}: {str(e)}")
        
        logger.info(f"Synced {success_count} leads to Mailchimp")
        return success_count > 0
    
    def sync_to_twilio(self, df: pd.DataFrame, message: str = None) -> bool:
        """Send SMS to leads via Twilio"""
        if not self.config['twilio_account_sid'] or self.config['twilio_account_sid'] == 'YOUR_TWILIO_SID':
            logger.warning("Twilio credentials not configured")
            return False
            
        from twilio.rest import Client
        
        if not message:
            message = """Stop Foreclosure Fast: We can help you avoid foreclosure and get cash for your home in 7 days. Call (555) STOP-NOW for a free consultation. Reply STOP to opt out."""
        
        client = Client(self.config['twilio_account_sid'], self.config['twilio_auth_token'])
        success_count = 0
        
        for _, row in df.iterrows():
            phone = row.get('phone')
            if not phone or len(phone) < 10:
                continue
                
            try:
                message_obj = client.messages.create(
                    body=message,
                    from_=self.config['twilio_phone_number'],
                    to=phone
                )
                success_count += 1
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Twilio SMS error for {phone}: {str(e)}")
        
        logger.info(f"Sent SMS to {success_count} leads via Twilio")
        return success_count > 0
    
    def sync_to_google_ads(self, df: pd.DataFrame) -> bool:
        """Create Google Ads Customer Match audience"""
        if not self.config['google_ads_customer_id'] or self.config['google_ads_customer_id'] == 'YOUR_CUSTOMER_ID':
            logger.warning("Google Ads credentials not configured")
            return False
            
        try:
            from google.ads.googleads.client import GoogleAdsClient
            
            # Initialize client
            credentials = {
                'developer_token': self.config['google_ads_developer_token'],
                'client_id': self.config['google_ads_client_id'],
                'client_secret': self.config['google_ads_client_secret'],
                'refresh_token': self.config['google_ads_refresh_token'],
            }
            
            client = GoogleAdsClient.load_from_dict(credentials)
            user_list_service = client.get_service("UserListService")
            
            # Create user list
            user_list_operation = client.get_type("UserListOperation")
            user_list = user_list_operation.create
            user_list.name = f"Foreclosure Leads {datetime.now().strftime('%Y-%m-%d')}"
            user_list.description = "Pre-foreclosure homeowners from Retran.com"
            user_list.membership_status = client.enums.UserListMembershipStatusEnum.OPEN
            user_list.membership_life_span = 365
            
            crm_based_user_list = user_list.crm_based_user_list
            crm_based_user_list.upload_key_type = client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
            
            response = user_list_service.mutate_user_lists(
                customer_id=self.config['google_ads_customer_id'],
                operations=[user_list_operation]
            )
            
            user_list_resource_name = response.results[0].resource_name
            
            # Add members to user list
            offline_user_data_job_service = client.get_service("OfflineUserDataJobService")
            
            # Create job
            offline_user_data_job = client.get_type("OfflineUserDataJob")
            offline_user_data_job.type_ = client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
            offline_user_data_job.customer_match_user_list_metadata.user_list = user_list_resource_name
            
            create_offline_user_data_job_response = offline_user_data_job_service.create_offline_user_data_job(
                customer_id=self.config['google_ads_customer_id'],
                job=offline_user_data_job
            )
            
            job_resource_name = create_offline_user_data_job_response.resource_name
            
            # Prepare user data
            operations = []
            for _, row in df.iterrows():
                if pd.isna(row.get('email')) and pd.isna(row.get('phone')):
                    continue
                    
                operation = client.get_type("OfflineUserDataJobOperation")
                user_data = operation.create
                
                if pd.notna(row.get('email')):
                    user_identifier = client.get_type("UserIdentifier")
                    user_identifier.hashed_email = hashlib.sha256(row['email'].lower().encode()).hexdigest()
                    user_data.user_identifiers.append(user_identifier)
                
                if pd.notna(row.get('phone')):
                    user_identifier = client.get_type("UserIdentifier")
                    user_identifier.hashed_phone_number = hashlib.sha256(row['phone'].encode()).hexdigest()
                    user_data.user_identifiers.append(user_identifier)
                
                operations.append(operation)
            
            # Upload data
            offline_user_data_job_service.add_offline_user_data_job_operations(
                resource_name=job_resource_name,
                operations=operations
            )
            
            # Run the job
            offline_user_data_job_service.run_offline_user_data_job(resource_name=job_resource_name)
            
            logger.info(f"Created Google Ads audience with {len(operations)} members")
            return True
            
        except Exception as e:
            logger.error(f"Google Ads sync error: {str(e)}")
            return False
    
    def sync_to_facebook_ads(self, df: pd.DataFrame) -> bool:
        """Create Facebook Custom Audience"""
        if not self.config['facebook_access_token'] or self.config['facebook_access_token'] == 'YOUR_FB_ACCESS_TOKEN':
            logger.warning("Facebook Ads credentials not configured")
            return False
            
        import hashlib
        
        url = f"https://graph.facebook.com/v18.0/{self.config['facebook_ad_account_id']}/customaudiences"
        
        # Create custom audience
        audience_data = {
            'name': f'Foreclosure Leads {datetime.now().strftime("%Y-%m-%d")}',
            'subtype': 'CUSTOM',
            'description': 'Pre-foreclosure homeowners from Retran.com',
            'customer_file_source': 'USER_PROVIDED_ONLY',
            'access_token': self.config['facebook_access_token']
        }
        
        try:
            response = requests.post(url, data=audience_data)
            if response.status_code != 200:
                logger.error(f"Facebook audience creation failed: {response.text}")
                return False
                
            audience_id = response.json()['id']
            
            # Prepare user data
            users = []
            for _, row in df.iterrows():
                user = {}
                
                if pd.notna(row.get('email')):
                    user['email'] = hashlib.sha256(row['email'].lower().encode()).hexdigest()
                
                if pd.notna(row.get('phone')):
                    user['phone'] = hashlib.sha256(row['phone'].encode()).hexdigest()
                
                if pd.notna(row.get('owner_name')):
                    name_parts = row['owner_name'].split()
                    if name_parts:
                        user['fn'] = hashlib.sha256(name_parts[0].lower().encode()).hexdigest()
                    if len(name_parts) > 1:
                        user['ln'] = hashlib.sha256(' '.join(name_parts[1:]).lower().encode()).hexdigest()
                
                if user:
                    users.append(user)
            
            # Upload users to audience
            upload_url = f"https://graph.facebook.com/v18.0/{audience_id}/users"
            upload_data = {
                'payload': {
                    'schema': list(users[0].keys()) if users else [],
                    'data': [list(user.values()) for user in users]
                },
                'access_token': self.config['facebook_access_token']
            }
            
            upload_response = requests.post(upload_url, json=upload_data)
            
            if upload_response.status_code == 200:
                logger.info(f"Created Facebook Custom Audience with {len(users)} members")
                return True
            else:
                logger.error(f"Facebook user upload failed: {upload_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Facebook Ads sync error: {str(e)}")
            return False
    
    def process_daily_leads(self, file_path: str, output_file: str = None) -> str:
        """Main processing function"""
        logger.info(f"Starting daily lead processing for {file_path}")
        
        try:
            # Load and clean data
            raw_df = self.load_retran_data(file_path)
            cleaned_df = self.clean_and_standardize(raw_df)
            
            # Enrich with emails
            enriched_df = self.enrich_leads(cleaned_df)
            
            # Sync to marketing platforms
            logger.info("Syncing to marketing platforms...")
            self.sync_to_mailchimp(enriched_df)
            time.sleep(2)
            
            self.sync_to_twilio(enriched_df)
            time.sleep(2)
            
            self.sync_to_google_ads(enriched_df)
            time.sleep(2)
            
            self.sync_to_facebook_ads(enriched_df)
            
            # Save enriched data
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f'enriched_leads_{timestamp}.csv'
            
            enriched_df.to_csv(output_file, index=False)
            logger.info(f"Processed leads saved to {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error in daily processing: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    processor = LeadProcessor()
    
    # Process today's Retran download
    input_file = "retran_download_today.csv"  # Replace with actual file path
    output_file = processor.process_daily_leads(input_file)
    
    print(f"Processing complete! Output saved to: {output_file}")