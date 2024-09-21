# Trinity Bot

Trinity Bot is a Discord bot that fetches frame data about **BlazBlue Centralfiction** and **BlazBlue Cross Tag Battle**.

![nine-6c](https://drive.google.com/u/0/drive-viewer/AKGpihbCbnkej4_ICbw5aZHMaOntMNXAlIKQojsYCTO9pgCWBxZFIgBEDE180kp3B3M4TeYOEJnvR-LXQvpRW1FsO5CJubyJtzNWZg=s2560)
## Getting Started

### Prerequisites

To host this bot yourself, you'll need the following:

- Python 3.8+
- `pycord` (Discord API wrapper)
- My database (download from the [releases page]())
- PostgreSQL (or your preferred database management system)

  
### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/trinity-bot.git
   cd trinity-bot
   ```
   
2. **Set Up Your Bot Token**:

- Set your environmental variable `TRINITY_TOKEN` to your bot token. You need one.
   
3. **Install Dependencies**:
   ```bash 
   pip install -r requirements.txt
   ```
   
4. **Set Up the Database**:

 - Download the database from the releases page.
 - Import the provided database into PostgreSQL (or your database of choice).
 - Update your database credentials in your environmental variable `DATABASE_SECRET`.

5. **Run it**:

- run `main.py`.
### Done!

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Darkened12/trinity-bot/blob/main/LICENSE) file for details.