import json
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import random
from collections import defaultdict

# --- First Code Block (Scraping) ---
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh;'
                          ' Intel Mac OS X 10_15_4)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/83.0.4103.97 Safari/537.36'}

def get_info(url):
    """ Get Information about the restaurant from URL """
    global headers
    try:
        webpage = requests.get(url, headers=headers, timeout=10) # Increased timeout
        webpage.raise_for_status() # Raise an exception for bad status codes
        html_text = BeautifulSoup(webpage.text, 'lxml')

        scripts = html_text.find_all('script', type='application/ld+json')
        info = None

        for script in scripts:
            try:
                parsed = json.loads(script.string)
                # Handle cases where the top level is an array of schemas
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and item.get('@type') in ['Restaurant', 'LocalBusiness']:
                             info = item
                             break
                elif isinstance(parsed, dict) and parsed.get('@type') in ['Restaurant', 'LocalBusiness']:
                    info = parsed
                    break
            except Exception:
                continue

        if not info:
            print(f"[WARNING] Structured data not found for URL: {url}")
            # Ensure the correct number of None values is returned based on columns
            return [None]*9 # 9 columns in the DataFrame

        address = info.get('address', {})
        #geo = info.get('geo', {}) # geo is not used in the current dataframe columns
        #rating = info.get('aggregateRating', {}) # rating is not used in the current dataframe columns


        data = (
            info.get('name'),
            info.get('openingHours'),
            address.get('streetAddress'),
            address.get('addressLocality'),
            address.get('addressRegion'),
            address.get('postalCode'),
            address.get('addressCountry'),
            info.get('telephone'),
            info.get('servesCuisine'),

        )
        return data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed for URL {url}: {e}")
        return [None]*9 # Return None for all expected columns on failure
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while processing {url}: {e}")
        return [None]*9 # Return None for all expected columns on other errors


def save_df(file_name, df):
    """ Save the dataframe """
    df.to_csv(file_name, index=False)
    print(f"Dataframe saved to {file_name}")


def get_restaurant_info(url_list, save=True, file_name="Restaurants.csv"):
    """ Get Restaurant Information from all urls passed """

    # Collecting the data
    data = []
    for url in url_list:
        data.append(get_info(url))

    # Creating the DataFrame
    # Ensure column count matches data returned by get_info
    columns = ['Name','Opening_Hours',
               'Street', 'Locality', 'Region', 'PostalCode', 'Country','Phone',
               'Cuisine']
    info_df = pd.DataFrame(data, columns=columns)

    # Save the df
    if save:
        save_df(file_name, info_df)

    return info_df

# --- Second Code Block (Knowledge Base) ---
class RestaurantKnowledgeBase:
    def __init__(self, csv_path):
        # Check if the CSV file exists before attempting to read
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Error: Input CSV file not found at {csv_path}")

        self.df = pd.read_csv(csv_path)
        # Convert NaN in Cuisine column to empty list for consistency before splitting
        self.df['Cuisine'] = self.df['Cuisine'].apply(lambda x: x.strip("[]").replace("'", "").split(', ') if pd.notna(x) else [])
        self.knowledge_base = defaultdict(dict)
        self.indexes = {
            'by_cuisine': defaultdict(list),
            'by_location': defaultdict(list),
            'by_opening_status': defaultdict(list),
            'by_price_range': defaultdict(list) # This index is built during build_knowledge_base
        }
        self.menu_templates = {
            'Chinese': [
                {"name": "Vegetable Spring Rolls", "price": 120, "category": "Starters"},
                {"name": "Chicken Manchurian", "price": 220, "category": "Main Course"},
                {"name": "Veg Fried Rice", "price": 180, "category": "Main Course"},
                {"name": "Chilli Chicken", "price": 250, "category": "Main Course"},
                {"name": "Schezwan Noodles", "price": 200, "category": "Main Course"}
            ],
            'North Indian': [
                {"name": "Paneer Tikka", "price": 220, "category": "Starters"},
                {"name": "Dal Makhani", "price": 180, "category": "Main Course"},
                {"name": "Butter Chicken", "price": 280, "category": "Main Course"},
                {"name": "Garlic Naan", "price": 50, "category": "Breads"},
                {"name": "Gulab Jamun", "price": 90, "category": "Desserts"}
            ],
            'Biryani': [
                {"name": "Vegetable Biryani", "price": 200, "category": "Main Course"},
                {"name": "Chicken Biryani", "price": 250, "category": "Main Course"},
                {"name": "Mutton Biryani", "price": 350, "category": "Main Course"},
                {"name": "Raita", "price": 60, "category": "Sides"},
                {"name": "Mirchi Ka Salan", "price": 80, "category": "Sides"}
            ],
            'Italian': [
                {"name": "Margherita Pizza", "price": 250, "category": "Main Course"},
                {"name": "Pasta Alfredo", "price": 220, "category": "Main Course"},
                {"name": "Garlic Bread", "price": 120, "category": "Starters"},
                {"name": "Tiramisu", "price": 150, "category": "Desserts"},
                {"name": "Minestrone Soup", "price": 160, "category": "Starters"}
            ],
            'Desserts': [
                {"name": "Chocolate Brownie", "price": 120, "category": "Desserts"},
                {"name": "Ice Cream Sundae", "price": 150, "category": "Desserts"},
                {"name": "Cheesecake", "price": 180, "category": "Desserts"},
                {"name": "Gajar Ka Halwa", "price": 100, "category": "Desserts"}
            ]
        }


    def _generate_menu(self, cuisines):
        """Generate a menu based on restaurant cuisines"""
        menu = []
        seen_items = set()

        # Handle cases where cuisines might be None or not iterable
        if not isinstance(cuisines, list):
             cuisines = []

        for cuisine in cuisines:
            base_cuisine = next((c for c in self.menu_templates.keys() if isinstance(cuisine, str) and c.lower() in cuisine.lower()), None)
            if base_cuisine:
                for item in self.menu_templates[base_cuisine]:
                    if item['name'] not in seen_items:
                        menu.append(item)
                        seen_items.add(item['name'])

        beverages = [
            {"name": "Mineral Water", "price": 30, "category": "Beverages"},
            {"name": "Fresh Lime Soda", "price": 60, "category": "Beverages"},
            {"name": "Masala Chai", "price": 40, "category": "Beverages"},
            {"name": "Cold Coffee", "price": 90, "category": "Beverages"}
        ]

        # Add some random beverages if the menu isn't too large already
        if len(menu) < 10: # Prevent adding too many beverages if base menu is large
             num_beverages = random.randint(1, min(len(beverages), 3)) # Add 1 to 3 beverages
             menu.extend(random.sample(beverages, num_beverages))


        if menu:
            prices = [item['price'] for item in menu]
            # Handle case where menu might be empty after filtering
            if prices:
                 min_price, max_price = min(prices), max(prices)
                 price_range = f"₹{min_price}-₹{max_price}"
            else:
                 price_range = "₹0-₹0" # Or some default range if no prices found
        else:
            price_range = "₹200-₹500" # Default range if no menu items generated

        return menu, price_range

    def _parse_opening_status(self, opening_str):
        """Determine if restaurant is open today"""
        if pd.isna(opening_str):
            return 'unknown'
        # Use regex for better matching and handle potential variations
        if re.search(r'\(Today\)', str(opening_str), re.IGNORECASE):
            return 'open_today'
        if re.search(r'Opens tomorrow', str(opening_str), re.IGNORECASE):
            return 'opens_tomorrow'
        # Could add more states like 'Closed' if detectable from string
        return 'unknown'

    def _normalize_opening_hours(self, opening_str):
        """Standardize opening hours format"""
        if pd.isna(opening_str):
            return None

        opening_str = str(opening_str) # Ensure it's a string

        tomorrow_match = re.match(r'Opens tomorrow at (\d+:\d+|\d+)\s*(am|pm)', opening_str, re.IGNORECASE)
        if tomorrow_match:
            time_part = tomorrow_match.group(1)
            period = tomorrow_match.group(2).lower()
            return f"Opens tomorrow at {time_part}{period}"

        if '(Today)' in opening_str:
            cleaned = opening_str.replace('(Today)', '').strip()
            cleaned = cleaned.replace('12midnight', '12:00am')
            cleaned = cleaned.replace('12noon', '12:00pm')
            cleaned = cleaned.replace('–', '-')
            # Optional: Add space before AM/PM if missing (e.g., "10:00am" -> "10:00 am")
            cleaned = re.sub(r'(\d)(am|pm)', r'\1 \2', cleaned, flags=re.IGNORECASE)
            return cleaned.strip()

        # Return original string if no specific pattern matched but it's not NaN
        return opening_str.strip()


    def preprocess_data(self):
        """Clean and normalize the raw data"""
        # Ensure columns exist before trying to process
        if 'Phone' in self.df.columns:
             self.df['Phone'] = self.df['Phone'].astype(str).str.replace('"', '').str.replace("'", "").str.strip() # Convert to str first
        else:
             self.df['Phone'] = None # Add column if missing

        # Cuisine splitting is now handled in __init__

        if 'Region' in self.df.columns:
             self.df['Region'] = self.df['Region'].astype(str).str.lower().str.strip()
        else:
             self.df['Region'] = None

        if 'Locality' in self.df.columns:
             self.df['Locality'] = self.df['Locality'].astype(str).str.lower().str.strip()
        else:
             self.df['Locality'] = None

        if 'Opening_Hours' in self.df.columns:
             self.df['Opening_Status'] = self.df['Opening_Hours'].apply(self._parse_opening_status)
             self.df['Opening_Hours_Normalized'] = self.df['Opening_Hours'].apply(self._normalize_opening_hours)
        else:
             self.df['Opening_Status'] = 'unknown'
             self.df['Opening_Hours_Normalized'] = None


        # Create Full_Address, handling potential None values in components
        address_cols = ['Street', 'Locality', 'Region', 'PostalCode', 'Country']
        for col in address_cols:
            if col not in self.df.columns:
                 self.df[col] = None # Add missing address columns

        self.df['Full_Address'] = self.df.apply(
            lambda row: ', '.join(str(row[col]).strip() for col in address_cols if pd.notna(row[col]) and str(row[col]).strip() != 'None'),
            axis=1
        ).replace('', None) # Replace empty strings with None if all parts were missing/None

        # Clean up 'Name' column
        if 'Name' in self.df.columns:
            self.df['Name'] = self.df['Name'].astype(str).str.strip()
        else:
            self.df['Name'] = None


    def build_knowledge_base(self):
        """Create structured knowledge base with indexing"""
        # Ensure data is preprocessed before building KB
        self.preprocess_data()

        for index, row in self.df.iterrows():
            # Skip rows where name is None or empty after processing
            if pd.isna(row['Name']) or row['Name'] == '':
                 print(f"[WARNING] Skipping row {index} due to missing name.")
                 continue

            restaurant_id = f"rest_{index}"
            menu, price_range = self._generate_menu(row['Cuisine'])

            # Safely get phone number(s)
            phone_numbers = [p.strip() for p in str(row['Phone']).split(',') if p.strip() != '' and p.strip() != 'nan'] if pd.notna(row['Phone']) else []
            if not phone_numbers:
                 phone_numbers = [None] # Ensure it's a list, even if empty

            # Build the restaurant entry
            self.knowledge_base[restaurant_id] = {
                'name': row['Name'],
                'address': {
                    'street': row['Street'] if pd.notna(row['Street']) else None,
                    'locality': row['Locality'] if pd.notna(row['Locality']) else None,
                    'region': row['Region'] if pd.notna(row['Region']) else None,
                    'postal_code': row['PostalCode'] if pd.notna(row['PostalCode']) else None,
                    'country': row['Country'] if pd.notna(row['Country']) else None,
                    'full_address': row['Full_Address']
                },
                'contact': {
                    'phone': phone_numbers
                },
                'cuisine': row['Cuisine'] if isinstance(row['Cuisine'], list) else [], # Ensure cuisine is a list
                'opening_info': {
                    'raw': row['Opening_Hours'] if pd.notna(row['Opening_Hours']) else None,
                    'normalized': row['Opening_Hours_Normalized'],
                    'status': row['Opening_Status']
                },
                'menu': menu,
                'price_range': price_range
            }

            # Update indexes
            for cuisine in row['Cuisine']:
                 if isinstance(cuisine, str) and cuisine.strip() != '': # Ensure cuisine is valid string
                     self.indexes['by_cuisine'][cuisine.lower().strip()].append(restaurant_id)

            if pd.notna(row['Locality']):
                 self.indexes['by_location'][row['Locality'].strip()].append(restaurant_id)

            self.indexes['by_opening_status'][row['Opening_Status']].append(restaurant_id)

            # Index by price range (using the generated one)
            self.indexes['by_price_range'][price_range].append(restaurant_id)


    def save_knowledge_base(self, file_name="restaurants.json"):
        """Save knowledge base to a JSON file"""
        try:
            output_data = {
                'restaurants': dict(self.knowledge_base), # Convert defaultdict to dict for JSON
                'indexes': dict(self.indexes) # Convert defaultdict to dict for JSON
            }

            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print(f"Knowledge base saved to {os.path.abspath(file_name)}")
            return True
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False


# --- Execution ---
if __name__ == "__main__":
    # Define the list of URLs to scrape
    urls = [
        'https://www.zomato.com/roorkee/tamarind-restaurant-roorkee-locality/order',
        'https://www.zomato.com/roorkee/olive-multicuisine-restaurant-roorkee-locality/order',
        'https://www.zomato.com/roorkee/rustic-house-roorkee-locality/order',
        'https://www.zomato.com/roorkee/hangries-roorkee-locality/order',
        'https://www.zomato.com/roorkee/milk-bar-roorkee-locality/order',
        'https://www.zomato.com/roorkee/desi-tadka-2-roorkee-locality/order',
        'https://www.zomato.com/roorkee/prakash-restaurant-roorkee-locality/order',
        'https://www.zomato.com/roorkee/hitchki-roorkee-locality/order',
        'https://www.zomato.com/roorkee/tanishas-restaurant-royal-hyderabadi-biryani-roorkee-locality/order',
        'https://www.zomato.com/roorkee/18-down-town-pool-restaurant-roorkee-locality/order'
    ]

    # Define the name for the intermediate CSV file
    csv_output_file = "Restaurants.csv"

    # --- Step 1: Scrape data and save to CSV ---
    print(f"Scraping data from {len(urls)} URLs...")
    restaurant_df = get_restaurant_info(urls, file_name=csv_output_file)

    # Check if the CSV was created and has data
    if os.path.exists(csv_output_file) and not restaurant_df.empty:
        print(f"Successfully scraped data and saved to {csv_output_file}.")

        # --- Step 2: Build knowledge base from the CSV and save to JSON ---
        print(f"\nBuilding knowledge base from {csv_output_file}...")
        try:
            # Initialize KnowledgeBase with the path to the CSV file
            kb = RestaurantKnowledgeBase(csv_output_file)
            # Preprocessing is now done within build_knowledge_base, but calling it explicitly here
            # is also fine if you want to separate concerns, but build_knowledge_base relies on it.
            # Let's keep the call in __init__ for robustness if preprocess_data is refactored later.
            # kb.preprocess_data() # Preprocessing happens in __init__ or start of build_knowledge_base

            kb.build_knowledge_base() # This now includes preprocessing steps

            # Define the name for the final JSON knowledge base file
            json_output_file = "restaurants.json"

            # Save the knowledge base to the specified JSON file
            if kb.save_knowledge_base(file_name=json_output_file):
                 print(f"Knowledge base successfully created and saved to {json_output_file}.")
            else:
                 print("Failed to save the knowledge base.")

        except FileNotFoundError:
            # This specific error is now checked in the KB constructor
            print(f"Error: Input CSV file not found at {csv_output_file}. Make sure the scraping step completed successfully.")
        except Exception as e:
            print(f"An unexpected error occurred during knowledge base creation: {e}")
    else:
        print(f"Scraping failed or returned no data. Cannot build knowledge base.")

