# Enhanced 3GPP PM Parser

A powerful and flexible parser for 3GPP Performance Measurement XML files, supporting multiple output formats and parallel processing.

## Features

- Parse single files or entire directories of 3GPP PM XML files
- Filter measurements by:
  - Measurement Info ID
  - P value
  - Object LDN
- Multiple output formats:
  - Excel (.xlsx)
  - SQLite database
  - CSV
- Parallel processing for improved performance
- Comprehensive error handling and logging
- Extensive test suite

## Installation

```bash
pip install enhanced-3gpp-pmparser
```

## Usage

### Command Line Interface

Basic usage:

```bash
# Process a single file
pmparser -f pm_file.xml -i measInfoId -p 1 -o excel

# Process all files in a directory
pmparser -d ./pm_files -i measInfoId -o sqlite

# Filter by specific Object LDNs
pmparser -f pm_file.xml -i measInfoId --objldn "obj1" --objldn "obj2"
```

Available options:

```
-f, --file         Single PM file to process
-d, --directory    Directory containing PM files
-i, --measinfoid   Measurement Info ID to filter
-p, --pvalue       P value to filter
--objldn           Object LDN to filter (can be specified multiple times)
-o, --output-type  Output format (excel, sqlite, csv)
--output-file      Output file name
-w, --workers      Number of worker processes
-v, --verbose      Enable verbose logging
```

### Python API

```python
from pmparser.core import PMParser, ParserConfig
from pmparser.output import OutputHandlerFactory

# Configure parser
config = ParserConfig(
    directory="./pm_files",
    measInfoId="example",
    p_value=1,
    output_type="excel"
)

# Initialize parser
parser = PMParser(config)

# Set output handler
output_handler = OutputHandlerFactory.create("excel", filename="output.xlsx")
parser.set_output_handler(output_handler)

# Process files
await parser.process_files()
```

## Development

### Setting up development environment

```bash
# Clone repository
git clone https://github.com/yourusername/enhanced-3gpp-pmparser.git
cd enhanced-3gpp-pmparser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"
```

### Running tests

```bash
python -m unittest discover tests
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have questions, please:

1. Check the documentation
2. Look for existing issues
3. Create a new issue if needed

## Acknowledgments

This project builds upon the excellent work done in various 3GPP PM parsing tools while adding modern features and improving performance.