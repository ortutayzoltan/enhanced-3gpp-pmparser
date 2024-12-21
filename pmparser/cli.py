#!/usr/bin/env python3
"""
Enhanced 3GPP PM Parser
Command-line interface for the PM Parser.
"""

import asyncio
import argparse
import logging
import sys
from typing import List

from .core import PMParser, ParserConfig, PMError
from .output import OutputHandlerFactory

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Enhanced 3GPP PM Parser',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-f', '--file',
        help='Single PM file to process'
    )
    input_group.add_argument(
        '-d', '--directory',
        help='Directory containing PM files'
    )
    
    parser.add_argument(
        '-i', '--measinfoid',
        help='Measurement Info ID to filter'
    )
    
    parser.add_argument(
        '-p', '--pvalue',
        type=int,
        help='P value to filter'
    )
    
    parser.add_argument(
        '--objldn',
        action='append',
        help='Object LDN to filter (can be specified multiple times)'
    )
    
    parser.add_argument(
        '-o', '--output-type',
        choices=['excel', 'sqlite', 'csv'],
        default='excel',
        help='Output format type'
    )
    
    parser.add_argument(
        '--output-file',
        help='Output file name'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of worker processes'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

async def main():
    """Main entry point"""
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('PMParser.CLI')
    
    try:
        # Create parser configuration
        config = ParserConfig(
            single_file=args.file,
            directory=args.directory,
            measInfoId=args.measinfoid,
            p_value=args.pvalue,
            objLdn_list=args.objldn,
            output_type=args.output_type,
            num_workers=args.workers
        )
        
        # Initialize parser
        parser = PMParser(config)
        
        # Set up output handler
        output_handler = OutputHandlerFactory.create(
            args.output_type,
            filename=args.output_file
        )
        parser.set_output_handler(output_handler)
        
        # Process files
        logger.info("Starting PM file processing...")
        results = await parser.process_files()
        logger.info(f"Successfully processed {len(results)} measurements")
        
    except PMError as e:
        logger.error(f"Parser error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())