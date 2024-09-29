# Generic YouTube Transcript Extractor

This application allows you to search for YouTube videos, extract their transcripts, and save them as text files. It provides a flexible interface that can be customized for various use cases.

## Features

- Search for YouTube videos based on queries and channels
- Extract and clean transcripts from videos
- Organize searches under customizable categories
- Schedule automatic searches
- Customizable labels for the user interface

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/generic-youtube-transcript-extractor.git
   cd generic-youtube-transcript-extractor
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python generic_transcript_extractor.py
   ```

2. In the application:
   - Use the "Admin" tab to customize labels if desired.
   - Add categories (called "Things" by default) in the main tab.
   - Add search queries to your categories.
   - Run searches manually or set up a schedule in the "Scheduler" tab.

3. Retrieved transcripts will be saved in the specified output directories.

## Customization

You can customize the labels used in the application by going to the "Admin" tab and changing the text for:
- The main category label (default: "Things")
- The "Add" button label
- The "Remove" button label

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.