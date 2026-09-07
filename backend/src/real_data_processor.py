"""
Phase 2 - Real Data Processor
Using Gemini 
"""

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import bigquery
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealDataProcessor:
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        vertexai.init(project=project_id, location="us-central1")
        self.model = GenerativeModel("gemini-1.5-flash")
        self.bq_client = bigquery.Client(project=project_id)
        logger.info("Real Data Processor initialized")
    
    def process(self):
        
        print("\n" + "="*60)
        print("PHASE 2 - PROCESSING REAL FILMMAKER DATA")
        print("="*60 + "\n")
        
        # Setup BigQuery
        print("Setting up BigQuery...")
        self._create_dataset()
        self._create_table()
        
        # Process scripts
        print("\nProcessing Scripts with Gemini...\n")
        scripts_folder = "assets/scripts"
        
        if os.path.exists(scripts_folder):
            script_files = [f for f in os.listdir(scripts_folder) if f.endswith('.pdf')]
            
            for script_file in script_files:
                script_path = os.path.join(scripts_folder, script_file)
                print(f"Analyzing: {script_file}")
                
                try:
                    result = self._analyze_script(script_path)
                    self._save_to_bigquery(result)
                    print(f"  Saved to BigQuery\n")
                except Exception as e:
                    print(f"  ERROR: {str(e)}\n")
        
        # Analyze videos
        print("Analyzing Videos with Gemini...\n")
        videos_folder = "assets/videos"
        
        if os.path.exists(videos_folder):
            video_files = [f for f in os.listdir(videos_folder) if f.endswith('.mp4')]
            print(f"Found {len(video_files)} videos\n")
            
            for video_file in video_files:
                video_path = os.path.join(videos_folder, video_file)
                print(f"Analyzing: {video_file}")
                print(f"  Video analysis requires upload to GCS (skipped for local)")
                print()
        
        print("="*60)
        print("PHASE 2 COMPLETE")
        print("="*60 + "\n")
    
    def _analyze_script(self, script_path: str) -> dict:
        """Analyze script with Gemini"""
        
        with open(script_path, 'rb') as f:
            script_data = f.read()
        
        script_file = Part.from_data(
            data=script_data,
            mime_type="application/pdf"
        )
        
        prompt = """Analyze this screenplay script:
1. Title/name of script
2. Number of scenes (count INT./EXT.)
3. Main characters (list up to 10)
4. Genre/type
5. Estimated page count
6. Summary of plot

Format as simple text."""
        
        response = self.model.generate_content([prompt, script_file])
        
        return {
            "file": os.path.basename(script_path),
            "analysis": response.text
        }
    
    def _create_dataset(self):
        """Create BigQuery dataset"""
        dataset_id = f"{self.project_id}.filmfund_data"
        
        try:
            self.bq_client.get_dataset(dataset_id)
            logger.info(f"Dataset exists: {dataset_id}")
        except:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            self.bq_client.create_dataset(dataset)
            logger.info(f"Created dataset: {dataset_id}")
    
    def _create_table(self):
        """Create scripts table"""
        table_id = f"{self.project_id}.filmfund_data.scripts"
        
        schema = [
            bigquery.SchemaField("file", "STRING"),
            bigquery.SchemaField("analysis", "STRING"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            self.bq_client.create_table(table)
            logger.info(f"Created table: {table_id}")
        except:
            logger.info(f"Table exists: {table_id}")
    
    def _save_to_bigquery(self, data: dict):
        """Save analysis to BigQuery"""
        table_id = f"{self.project_id}.filmfund_data.scripts"
        
        rows = [data]
        self.bq_client.insert_rows_json(table_id, rows)


def main():
    system = RealDataProcessor("film-fund")
    system.process()


if __name__ == "__main__":
    main()