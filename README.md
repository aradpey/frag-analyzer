# Fragrantica Review Analyzer

A web application that scrapes and analyzes perfume reviews from Fragrantica.com using GPT-4, providing detailed insights into fragrances through multiple analysis modules.


https://github.com/user-attachments/assets/3f3c4a91-f4cd-4692-b4ae-0aec04ef6c17


## Features

### 1. Review Scraping

- Automatically extracts reviews from any Fragrantica perfume page
- Captures perfume images and metadata
- Handles pagination and data cleaning
- Real-time progress tracking

### 2. Analysis Modules

Each module provides specialized analysis of different aspects:

#### Seasonal Wear Analysis

- Identifies primary and secondary seasons
- Based on explicit mentions and context
- Categorizes into Spring, Summer, Fall, Winter

#### Time of Day Analysis

- Determines optimal wearing times
- Analyzes versatility across different times
- Categories: Morning, Day, Afternoon, Evening, Night

#### Occasions Analysis

- Identifies suitable wearing occasions
- Extracts both social settings and specific events
- Provides context-aware recommendations

#### Fragrance Comparisons

- Identifies mentioned fragrances in reviews
- Analyzes similarities and differences
- Provides detailed comparison context
- Extracts specific note comparisons

#### Performance Analysis

- Evaluates longevity (with specific hour ranges)
- Analyzes sillage (from Intimate to Enormous)
- Assesses projection characteristics
- Provides consensus-based conclusions

#### Gender Classification

- Determines gender perception
- Analyzes versatility across gender preferences
- Considers cultural and temporal context

#### Summary Generation

- Creates concise, informative summaries
- Highlights key characteristics
- Emphasizes distinctive features

### 3. User Interface

- Clean, modern design
- Responsive layout
- Real-time analysis updates
- Collapsible sections
- Interactive review display
- Performance statistics

## Technical Stack

### Backend

- Python 3.8+
- Flask web framework
- OpenAI GPT-4 API
- BeautifulSoup4 for web scraping
- Requests for HTTP handling
- Logging for operation tracking

### Frontend

- HTML5
- CSS3 with modern animations
- Vanilla JavaScript
- Responsive design
- Progressive loading

## Installation

1. Clone the repository:

```bash
git clone https://github.com/aradpey/frag-analyzer.git
cd frag-analyzer
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory with:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://localhost:5001
```

3. Enter a Fragrantica perfume URL and click "Analyze Fragrance"

## API Response Format

Each analysis module returns structured JSON data:

### Seasonal Wear

```json
{
  "primary": ["Winter", "Fall"],
  "secondary": ["Spring"]
}
```

### Time of Day

```json
{
  "best_times": ["Evening", "Night"],
  "versatility": "Moderately Versatile"
}
```

### Performance

```json
{
  "longevity": {
    "conclusion": "6-8 hours",
    "analysis": "Detailed analysis..."
  },
  "sillage": {
    "conclusion": "Strong",
    "analysis": "Detailed analysis..."
  },
  "projection": {
    "conclusion": "Good Projection",
    "analysis": "Detailed analysis..."
  }
}
```

## Error Handling

- Comprehensive error handling for network issues
- Graceful degradation for API failures
- User-friendly error messages
- Detailed logging for debugging

## Security Considerations

- API key protection through environment variables
- Input validation and sanitization
- Rate limiting for API calls
- Error message sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Fragrantica.com for the perfume data
- OpenAI for GPT-4 API
- The Flask team for the web framework
- Beautiful Soup team for HTML parsing

## Future Enhancements

- [ ] Add support for multiple languages
- [ ] Implement caching for repeated analyses
- [ ] Add historical data tracking
- [ ] Implement user accounts and saved analyses
- [ ] Add comparative analysis between fragrances
- [ ] Enhance mobile responsiveness
- [ ] Add export functionality for analyses

## Support

For support, please open an issue in the [GitHub repository](https://github.com/aradpey/frag-analyzer/issues) or contact ahouraradpey@gmail.com.
