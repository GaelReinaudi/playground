"""
Script to scrape ski resort status information and generate reports and social media posts
using a hierarchical agent approach.
"""

import os
from typing import Dict, List, Optional, Union
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag
from langchain_openai import ChatOpenAI  # Updated import
from langchain_core.messages import HumanMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.tools import Tool
from langchain import hub
from dotenv import load_dotenv
import graphviz

# Load environment variables
load_dotenv()

class YukiyamaAPI:
    """Client for the Yukiyama API."""
    
    BASE_URL = "https://web-api.yukiyama.biz/web-api/latest-facility/backward"
    SKI_AREAS = {
        379: "Grand Hirafu",
        390: "Hanazono",
        391: "Niseko Village",
        394: "Annupuri"
    }
    
    @classmethod
    def get_lift_status(cls, area_id: int) -> Dict:
        """Get lift status for a specific ski area."""
        params = {
            "facilityType": "lift",
            "lang": "en",
            "skiareaId": area_id
        }
        try:
            response = requests.get(cls.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "area_name": cls.SKI_AREAS.get(area_id, f"Area {area_id}"),
                "lifts": data.get("results", []),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "area_name": cls.SKI_AREAS.get(area_id, f"Area {area_id}"),
                "error": str(e)
            }

class ResortScraper:
    """Handles scraping of ski resort websites."""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Clean scraped text by removing extra whitespace and newlines."""
        if not text:
            return ""
        return " ".join(text.split())
    
    @staticmethod
    def safe_get_text(element: Optional[Tag]) -> str:
        """Safely get text from a BeautifulSoup element."""
        if element and hasattr(element, 'get_text'):
            return element.get_text()
        return ""
    
    @classmethod
    def get_all_niseko_data(cls) -> Dict:
        """Get combined data from scraping and API for all Niseko areas."""
        # Get API data for all areas
        api_data = {}
        for area_id in [379, 390, 391, 394]:  # Grand Hirafu, Hanazono, Niseko Village, Annupuri
            area_data = YukiyamaAPI.get_lift_status(area_id)
            api_data[area_data['area_name']] = area_data
        
        # Get website data
        website_data = cls.scrape_niseko()
        
        return {
            "resort": "Niseko United",
            "api_data": api_data,
            "website_data": website_data,
            "timestamp": datetime.now().isoformat()
        }

    @classmethod
    def scrape_niseko(cls) -> Dict:
        """Scrape Niseko resort status."""
        url = "https://www.niseko.ne.jp/en/niseko-lift-status/"
        try:
            response = requests.get(url, headers=cls.HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract specific sections
            weather_info = {}
            trail_info = []
            
            # Look for weather information
            weather_div = soup.find('div', class_='weather-info')
            if isinstance(weather_div, Tag):
                temp = weather_div.find('div', class_='temperature')
                if isinstance(temp, Tag):
                    weather_info['temperature'] = cls.clean_text(cls.safe_get_text(temp))
                
                conditions = weather_div.find('div', class_='conditions')
                if isinstance(conditions, Tag):
                    weather_info['conditions'] = cls.clean_text(cls.safe_get_text(conditions))
            
            # Look for trail information
            trail_divs = soup.find_all('div', class_='trail-status')
            for div in trail_divs:
                if isinstance(div, Tag):
                    trail_name = div.find('div', class_='trail-name')
                    trail_condition = div.find('div', class_='trail-condition')
                    if isinstance(trail_name, Tag) and isinstance(trail_condition, Tag):
                        trail_info.append({
                            "name": cls.clean_text(cls.safe_get_text(trail_name)),
                            "condition": cls.clean_text(cls.safe_get_text(trail_condition))
                        })
            
            return {
                "weather": weather_info,
                "trails": trail_info,
            }
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def scrape_rusutsu(cls) -> Dict:
        """Scrape Rusutsu resort status."""
        url = "https://rusutsu.com/en/lift-and-trail-status/"
        try:
            response = requests.get(url, headers=cls.HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract specific sections
            lift_status = []
            weather_info = {}
            trail_info = []
            
            # Look for lift status information
            lift_section = soup.find('section', id='lift-status')
            if isinstance(lift_section, Tag):
                lift_items = lift_section.find_all('div', class_='lift-item')
                for item in lift_items:
                    if isinstance(item, Tag):
                        name = item.find('div', class_='lift-name')
                        status = item.find('div', class_='lift-status')
                        if isinstance(name, Tag) and isinstance(status, Tag):
                            lift_status.append({
                                "name": cls.clean_text(cls.safe_get_text(name)),
                                "status": cls.clean_text(cls.safe_get_text(status))
                            })
            
            # Look for weather information
            weather_section = soup.find('section', id='weather')
            if isinstance(weather_section, Tag):
                temp = weather_section.find('div', class_='temperature')
                if isinstance(temp, Tag):
                    weather_info['temperature'] = cls.clean_text(cls.safe_get_text(temp))
                
                conditions = weather_section.find('div', class_='conditions')
                if isinstance(conditions, Tag):
                    weather_info['conditions'] = cls.clean_text(cls.safe_get_text(conditions))
            
            # Look for trail information
            trail_section = soup.find('section', id='trail-status')
            if isinstance(trail_section, Tag):
                trail_items = trail_section.find_all('div', class_='trail-item')
                for item in trail_items:
                    if isinstance(item, Tag):
                        name = item.find('div', class_='trail-name')
                        condition = item.find('div', class_='trail-condition')
                        if isinstance(name, Tag) and isinstance(condition, Tag):
                            trail_info.append({
                                "name": cls.clean_text(cls.safe_get_text(name)),
                                "condition": cls.clean_text(cls.safe_get_text(condition))
                            })
            
            return {
                "resort": "Rusutsu",
                "data": {
                    "lift_status": lift_status,
                    "weather": weather_info,
                    "trails": trail_info
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"resort": "Rusutsu", "error": str(e)}

class StatusAnalyzer:
    """Analyzes scraped data to extract meaningful status information."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def analyze_niseko_data(self, resort_data: Dict) -> Dict:
        """Analyze Niseko resort data from both API and website."""
        if "error" in resort_data.get("website_data", {}):
            return resort_data
        
        # Create a more structured analysis prompt
        prompt = f"""
        Analyze the following Niseko United ski resort data and create a concise summary:

        API Data for Each Area:
        {resort_data['api_data']}

        Website Weather Information:
        {resort_data['website_data'].get('weather', {})}

        Website Trail Conditions:
        {resort_data['website_data'].get('trails', [])}

        Please provide a summary that includes:
        1. Overall resort status for each area (open/closed/partial)
        2. Number of operational lifts in each area
        3. General trail conditions
        4. Current weather conditions
        5. Any notable highlights or warnings
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {
            "resort": resort_data["resort"],
            "analysis": response.content,
            "timestamp": resort_data["timestamp"]
        }
    
    def analyze_rusutsu_data(self, resort_data: Dict) -> Dict:
        """Analyze Rusutsu resort data."""
        if "error" in resort_data:
            return resort_data
        
        prompt = f"""
        Analyze the following Rusutsu resort data and create a concise summary:

        Lift Status:
        {resort_data['data']['lift_status']}

        Weather Information:
        {resort_data['data']['weather']}

        Trail Conditions:
        {resort_data['data']['trails']}

        Please provide a summary that includes:
        1. Overall resort status (open/closed/partial)
        2. Number of operational lifts
        3. General trail conditions
        4. Current weather conditions
        5. Any notable highlights or warnings
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {
            "resort": resort_data["resort"],
            "analysis": response.content,
            "timestamp": resort_data["timestamp"]
        }

class ContentGenerator:
    """Generates reports and social media content."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate_report(self, analyses: List[Dict]) -> str:
        """Generate a detailed report from the analyses."""
        prompt = f"""
        Create a professional ski resort status report based on the following analyses:
        {analyses}
        
        Format the report with the following sections for each resort:
        1. Resort Name
        2. Current Status Overview
        3. Lift Operations with emojis (red for closed, green for open, yellow for partial)
        4. Trail Conditions
        5. Weather Report
        6. Special Notices (if any)
        
        Use markdown formatting to make the report easy to read.
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def generate_social_post(self, analyses: List[Dict]) -> str:
        """Generate an engaging social media post."""
        prompt = f"""
        Create an exciting and informative social media post about the current ski conditions for each resort:
        {analyses}
        
        Requirements:
        1. Must be under 1000 characters
        2. Include relevant emoji
        3. Highlight the most exciting or notable conditions
        4. Use hashtags: #NisekoUnited #Rusutsu #Skiing #JapanPow
        5. Make it engaging and action-oriented
        6. Mention any special conditions in different areas
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

class WorkflowVisualizer:
    """Visualizes the workflow structure of the ski status reporting system."""
    
    @staticmethod
    def create_graph() -> graphviz.Digraph:
        """Create a detailed graph of the workflow."""
        dot = graphviz.Digraph(comment='Ski Status Workflow')
        dot.attr(rankdir='TB')
        
        # Add nodes with clusters for each major component
        with dot.subgraph(name='cluster_0') as c:
            c.attr(label='Data Sources')
            c.attr(style='filled')
            c.attr(color='lightgrey')
            c.node('yukiyama_api', 'Yukiyama API\n(4 Areas)', shape='cylinder')
            c.node('niseko_web', 'Niseko Website\n(Weather & Trails)', shape='cylinder')
            c.node('rusutsu_web', 'Rusutsu Website\n(All Data)', shape='cylinder')
        
        with dot.subgraph(name='cluster_1') as c:
            c.attr(label='Data Collection')
            c.attr(style='filled')
            c.attr(color='lightblue')
            c.node('scraper', 'ResortScraper\nClass', shape='component')
            c.node('api_client', 'YukiyamaAPI\nClass', shape='component')
        
        with dot.subgraph(name='cluster_2') as c:
            c.attr(label='Data Processing')
            c.attr(style='filled')
            c.attr(color='lightgreen')
            c.node('analyzer', 'StatusAnalyzer\nClass', shape='component')
            c.node('llm', 'ChatOpenAI\nLLM', shape='diamond')
        
        with dot.subgraph(name='cluster_3') as c:
            c.attr(label='Content Generation')
            c.attr(style='filled')
            c.attr(color='lightyellow')
            c.node('content_gen', 'ContentGenerator\nClass', shape='component')
            c.node('report', 'Detailed\nReport', shape='note')
            c.node('social', 'Social Media\nPost', shape='note')
        
        # Add edges to show data flow
        dot.edge('yukiyama_api', 'api_client', 'JSON Data')
        dot.edge('niseko_web', 'scraper', 'HTML')
        dot.edge('rusutsu_web', 'scraper', 'HTML')
        
        dot.edge('api_client', 'analyzer', 'Lift Status')
        dot.edge('scraper', 'analyzer', 'Weather & Trail Info')
        
        dot.edge('analyzer', 'llm', 'Raw Data')
        dot.edge('llm', 'analyzer', 'Analysis')
        
        dot.edge('analyzer', 'content_gen', 'Analysis Results')
        dot.edge('content_gen', 'report', 'Markdown')
        dot.edge('content_gen', 'social', 'Text')
        
        return dot

def visualize_workflow():
    """Create and save the workflow visualization."""
    dot = WorkflowVisualizer.create_graph()
    # Save in the current directory
    output_base = os.path.join(os.path.dirname(__file__), 'ski_status_workflow')
    # Save as both PNG and PDF for different use cases
    dot.render(output_base, format='png', cleanup=True)
    dot.render(output_base, format='pdf', cleanup=True)
    print(f"\nWorkflow visualization saved as '{output_base}.png' and '{output_base}.pdf'")

def main():
    # Initialize LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Initialize components
    scraper = ResortScraper()
    analyzer = StatusAnalyzer(llm)
    content_gen = ContentGenerator(llm)
    
    # Create workflow visualization
    print("Generating workflow visualization...")
    visualize_workflow()
    
    # Execute the workflow
    try:
        # Scrape data
        print("\nGathering Niseko United data (API + Website)...")
        niseko_data = scraper.get_all_niseko_data()
        print("Scraping Rusutsu resort data...")
        rusutsu_data = scraper.scrape_rusutsu()
        
        # Analyze data
        print("\nAnalyzing resort data...")
        niseko_analysis = analyzer.analyze_niseko_data(niseko_data)
        rusutsu_analysis = analyzer.analyze_rusutsu_data(rusutsu_data)
        analyses = [niseko_analysis, rusutsu_analysis]
        
        # Generate content
        print("\nGenerating report and social media post...")
        report = content_gen.generate_report(analyses)
        social_post = content_gen.generate_social_post(analyses)
        
        # Output results
        print("\n=== Detailed Report ===")
        print(report)
        print("\n=== Social Media Post ===")
        print(social_post)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()