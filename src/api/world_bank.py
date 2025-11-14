"""
World Bank API Client
Fetches macroeconomic indicators from the World Bank Open Data API
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
import time


class WorldBankAPI:
    """Client for interacting with World Bank API"""
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    # World Bank Indicator Codes
    INDICATORS = {
        "gdp": "NY.GDP.MKTP.CD",  # GDP (current US$)
        "inflation": "FP.CPI.TOTL.ZG",  # Inflation, consumer prices (annual %)
        "unemployment": "SL.UEM.TOTL.ZS"  # Unemployment, total (% of total labor force)
    }
    
    # Popular countries for quick selection
    POPULAR_COUNTRIES = {
        "USA": "United States",
        "CHN": "China",
        "JPN": "Japan",
        "DEU": "Germany",
        "GBR": "United Kingdom",
        "IND": "India",
        "FRA": "France",
        "BRA": "Brazil",
        "ITA": "Italy",
        "CAN": "Canada",
        "KOR": "Korea, Rep.",
        "RUS": "Russian Federation",
        "AUS": "Australia",
        "MEX": "Mexico",
        "IDN": "Indonesia",
        "NLD": "Netherlands",
        "SAU": "Saudi Arabia",
        "TUR": "Turkey",
        "CHE": "Switzerland",
        "POL": "Poland",
        "ESP": "Spain",
        "ZAF": "South Africa",
        "ARG": "Argentina",
        "NGA": "Nigeria",
        "EGY": "Egypt, Arab Rep."
    }
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_indicator(
        self,
        indicator_code: str,
        country_codes: List[str],
        start_year: int = 2000,
        end_year: int = 2023
    ) -> pd.DataFrame:
        """
        Fetch indicator data for specified countries and years
        
        Args:
            indicator_code: World Bank indicator code
            country_codes: List of ISO country codes (e.g., ['USA', 'CHN'])
            start_year: Starting year for data
            end_year: Ending year for data
            
        Returns:
            DataFrame with columns: country, country_code, year, value
        """
        all_data = []
        
        for country_code in country_codes:
            try:
                data = self._fetch_country_indicator(
                    indicator_code, 
                    country_code, 
                    start_year, 
                    end_year
                )
                all_data.extend(data)
                time.sleep(0.1)  # Rate limiting - be nice to the API
            except Exception as e:
                print(f"Error fetching data for {country_code}: {e}")
                continue
        
        if not all_data:
            return pd.DataFrame(columns=['country', 'country_code', 'year', 'value'])
        
        df = pd.DataFrame(all_data)
        df = df.sort_values(['country', 'year']).reset_index(drop=True)
        return df
    
    def _fetch_country_indicator(
        self,
        indicator_code: str,
        country_code: str,
        start_year: int,
        end_year: int
    ) -> List[Dict]:
        """Fetch data for a single country"""
        
        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        params = {
            "date": f"{start_year}:{end_year}",
            "format": "json",
            "per_page": 1000
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        json_data = response.json()
        
        # World Bank API returns [metadata, data] array
        if len(json_data) < 2 or json_data[1] is None:
            return []
        
        data_records = []
        for entry in json_data[1]:
            if entry['value'] is not None:
                data_records.append({
                    'country': entry['country']['value'],
                    'country_code': entry['countryiso3code'],
                    'year': int(entry['date']),
                    'value': float(entry['value'])
                })
        
        return data_records
    
    def fetch_gdp(
        self,
        country_codes: List[str],
        start_year: int = 2000,
        end_year: int = 2023
    ) -> pd.DataFrame:
        """Fetch GDP data"""
        return self.fetch_indicator(
            self.INDICATORS['gdp'],
            country_codes,
            start_year,
            end_year
        )
    
    def fetch_inflation(
        self,
        country_codes: List[str],
        start_year: int = 2000,
        end_year: int = 2023
    ) -> pd.DataFrame:
        """Fetch inflation data"""
        return self.fetch_indicator(
            self.INDICATORS['inflation'],
            country_codes,
            start_year,
            end_year
        )
    
    def fetch_unemployment(
        self,
        country_codes: List[str],
        start_year: int = 2000,
        end_year: int = 2023
    ) -> pd.DataFrame:
        """Fetch unemployment data"""
        return self.fetch_indicator(
            self.INDICATORS['unemployment'],
            country_codes,
            start_year,
            end_year
        )
    
    def get_all_countries(self) -> Dict[str, str]:
        """
        Fetch list of all countries from World Bank API
        
        Returns:
            Dictionary mapping country codes to country names
        """
        url = f"{self.BASE_URL}/country"
        params = {
            "format": "json",
            "per_page": 500
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            json_data = response.json()
            
            if len(json_data) < 2:
                return self.POPULAR_COUNTRIES
            
            countries = {}
            for country in json_data[1]:
                # Filter out regions and aggregates
                if country['capitalCity']:  # Only actual countries have capitals
                    code = country['iso2Code']
                    name = country['name']
                    if len(code) == 2 or len(code) == 3:  # Valid country codes
                        countries[code] = name
            
            return countries if countries else self.POPULAR_COUNTRIES
            
        except Exception as e:
            print(f"Error fetching countries: {e}")
            return self.POPULAR_COUNTRIES


# Singleton instance
wb_api = WorldBankAPI()
