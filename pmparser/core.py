#!/usr/bin/env python3
"""
Enhanced 3GPP PM Parser
Core implementation module containing the main parser logic.
"""

import asyncio
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from multiprocessing import cpu_count
from typing import Dict, List, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('PMParser')

# Constants
NAMESPACE = '{http://www.3gpp.org/ftp/specs/archive/32_series/32.435#measCollec}'
DEFAULT_FILE_PATTERN = r'A.*\.xml'

@dataclass
class ParserConfig:
    """Configuration class for the PM Parser"""
    single_file: Optional[str] = None
    directory: Optional[str] = None
    file_pattern: str = DEFAULT_FILE_PATTERN
    measInfoId: Optional[str] = None
    p_value: Optional[int] = None
    objLdn_list: List[str] = None
    output_type: str = 'excel'
    num_workers: int = None

    def __post_init__(self):
        if self.num_workers is None:
            self.num_workers = cpu_count()
        if self.objLdn_list is None:
            self.objLdn_list = []

class PMError(Exception):
    """Custom exception class for PM Parser errors"""
    pass

class XMLProcessor:
    """Handles XML file processing"""
    
    def __init__(self, namespace: str = NAMESPACE):
        self.namespace = namespace

    def create_xpath_string(self, element: str, **kwargs) -> str:
        """Create XPath string for XML element with optional attributes"""
        base = f'.//{self.namespace}{element}'
        attrs = []
        for key, value in kwargs.items():
            if value is not None:
                attrs.append(f'@{key}="{value}"')
        if attrs:
            return f'{base}[{" and ".join(attrs)}]'
        return base

    async def process_file(self, file_path: str, config: ParserConfig) -> List[Dict]:
        """Process a single XML file and return measurement data"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            results = []
            for measInfo in root.findall(self.create_xpath_string('measInfo')):
                if config.measInfoId and measInfo.get('measInfoId') != config.measInfoId:
                    continue
                    
                granPeriod = measInfo.find(self.create_xpath_string('granPeriod'))
                endTime = granPeriod.get('endTime')
                
                # Process measurement types
                meas_types = {
                    mt.get('p'): mt.text 
                    for mt in measInfo.findall(self.create_xpath_string('measType'))
                }
                
                # Process measurement values
                for measValue in measInfo.findall(self.create_xpath_string('measValue')):
                    obj_ldn = measValue.get('measObjLdn')
                    
                    if config.objLdn_list and obj_ldn not in config.objLdn_list:
                        continue
                        
                    for r in measValue.findall(self.create_xpath_string('r')):
                        p = r.get('p')
                        if config.p_value and p != str(config.p_value):
                            continue
                            
                        try:
                            value = float(r.text)
                        except (ValueError, TypeError):
                            value = r.text
                            
                        results.append({
                            'endTime': endTime,
                            'measInfoId': measInfo.get('measInfoId'),
                            'measObjLdn': obj_ldn,
                            'p': int(p),
                            'value': value,
                            'measType': meas_types.get(p)
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise PMError(f"Failed to process {file_path}: {str(e)}")

class PMParser:
    """Main Parser class"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.xml_processor = XMLProcessor()
        self.output_handler = None

    def set_output_handler(self, handler):
        """Set the output handler for processed data"""
        self.output_handler = handler

    async def _get_files_to_process(self) -> List[str]:
        """Get list of files to process based on configuration"""
        if self.config.single_file:
            if not os.path.exists(self.config.single_file):
                raise PMError(f"File not found: {self.config.single_file}")
            return [self.config.single_file]
            
        if self.config.directory:
            if not os.path.exists(self.config.directory):
                raise PMError(f"Directory not found: {self.config.directory}")
            pattern = re.compile(self.config.file_pattern)
            return [
                os.path.join(self.config.directory, f)
                for f in os.listdir(self.config.directory)
                if pattern.match(f)
            ]
            
        raise PMError("No input file or directory specified")

    async def process_files(self):
        """Process all files according to configuration"""
        files = await self._get_files_to_process()
        if not files:
            raise PMError("No files found to process")

        logger.info(f"Processing {len(files)} files with {self.config.num_workers} workers")
        
        results = []
        with ProcessPoolExecutor(max_workers=self.config.num_workers) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    self.xml_processor.process_file,
                    file,
                    self.config
                )
                for file in files
            ]
            
            for future in asyncio.as_completed(futures):
                try:
                    result = await future
                    results.extend(result)
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")

        if self.output_handler:
            await self.output_handler.write(results)
        
        return results

if __name__ == "__main__":
    # Example usage
    config = ParserConfig(
        directory="./data",
        measInfoId="example",
        output_type="excel"
    )
    
    parser = PMParser(config)
    asyncio.run(parser.process_files())