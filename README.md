# League of Legends Statistics

This project is a web application that provides personal statistics and data for League of Legends champions by role, including runepages, item statistics, and more.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Acknowledgments](#acknowledgments)

## Description

League of Legends Statistics is a Flask-based web application designed to provide detailed statistical data for League of Legends champions. The app includes features such as:

- Runepage Data (Best Winrate, Recommended Runepage, Runepage with Most Games Played)
- Resource Management Data (Gold and CS)
- Combat Statistics (Damage and KDA)
- Objective Control Data (Dragons, Barons, Grubs etc.)
- Item Winrate Data 

## Installation

To get a local copy up and running, follow these steps.

### Prerequisites

- Python 3.8+
- Flask
- Pandas


### Installation Steps

1. Clone the repository
    ```sh
    git clone https://github.com/Ferix8475/LoL.git
    ```
2. Navigate to the project directory
    ```sh
    cd LoL
    ```
3. Install the dependencies
    ```sh
    pip install -r requirements.txt
    ```

4. Run the setup file, and enter your Riot API Key and Riot ID. See [here](https://developer.riotgames.com/docs/portal) to see how to get an API Key. Note that this might take a while due to API Rate Limits. Also note that Development API Keys only last 24hrs, so you will have to refresh it every time you run this command.

    ```sh
    python setup.py
    ```

5. Run the application
    ```sh
    flask run
    ```

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:5000/`.

2. Use the search functionality to find statistics for a specific champion.
3. Browse through different sections like runepages, resource management data, combat statistics, item winrate statistics, and more.
4. To update the dataframe with the most recent matches you've played, run the following command, and enter your Riot API Key. See [here](https://developer.riotgames.com/docs/portal) to see how to get an API Key. Note that this might take a while due to API Rate Limits. Also note that Development API Keys only last 24hrs, so you will have to refresh it every time you run this command.
    ```
    python update.py
    ```
5. To reset which Riot User's data you wish to look at, simply rerun [step 6 from the installation steps](#installation) with the new Riot ID.

## License

Distributed under the MIT License. See `LICENSE` for more information.


## Acknowledgments

- [League of Legends API](https://developer.riotgames.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Data Dragon](https://riot-api-libraries.readthedocs.io/en/latest/ddragon.html)
- [Community Dragon](https://www.communitydragon.org/)
