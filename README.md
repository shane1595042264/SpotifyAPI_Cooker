
Inspiration 🌟
--------------

In the fast-paced world of pop music, we often forget the songs that once defined our time. Inspired by the time capsule, we envisioned a space where users could journey back in time, rediscovering the top tracks that shaped each year. We also made a user profile for each user to explore their time capsules.

What it does 🎵
---------------

Music Cooker offers an interactive experience where users can slide through the years, from 1900 to the present, witnessing the evolution of music. Each year, the platform showcases the top tracks with their popularity rankings and artist details. As an added layer of immersion, it tracks autoplay, allowing users to see and hear the essence of each year. Other than that, we also have a search bar for users to find the statistics of the specific artists they like. It also has a profile page for current users.

How we built it 🔧
------------------

The project harnesses Flask for the backend, sourcing data from the Spotify API. For visualization, we integrated Plotly.js, crafting interactive charts that react in real time to user actions. The front end blends HTML, CSS, and JavaScript, ensuring a seamless and engaging user experience.

Challenges we ran into 🚧
-------------------------

Merging the autoplay feature for tracks with user intuition was a tricky endeavor. Ensuring the real-time responsiveness of the charts while upholding performance posed another challenge. But with persistent testing and optimizations, we carved out a smooth experience.

Accomplishments that we're proud of 🏆
--------------------------------------

Successfully visualizing over a century's worth of music data interactively stands as our crowning achievement. Despite its initial challenges, the autoplay feature adds a dimension to the user experience, making the musical journey through time audibly tangible.

What we learned 📚
------------------

Our deep dive into the Spotify API unraveled the intricacies of fetching and manipulating musical data. The project also illuminated the art of crafting user-centric designs where functionality intertwines with intuition.

What's next for Music Cooker 🔮
-------------------------------

I am setting on more granular data integration, zooming into monthly or weekly top tracks. A lyrical analysis showcasing the thematic evolution in music looms on the horizon. The project also needs time to set up the OAuth 2.0 for the Spotify API to get to the current user's profile.

### Step-by-Step Guide 

**Written with the help of ChatGPT**

1.  Clone the Repository:

    Use `git` to clone the repository to your local machine.



    `git clone https://github.com/shane1595042264/SpotifyAPI_Cooker.git`

2.  Navigate to the Project Directory:

    Change into the project directory.

    `cd SpotifyAPI_Cooker/backend`

3.  Set Up a Virtual Environment:

    Create a new virtual environment inside the project directory.


    `virtualenv venv`

4.  Activate the Virtual Environment:

    Depending on your operating system:

    -   Linux or macOS:

    

        `source venv/bin/activate`

    -   Windows (Command Prompt):

    

        `venv\Scripts\activate`

    -   Windows (PowerShell):

    

        `.\venv\Scripts\Activate`

5.  Install Required Packages:

    With the virtual environment activated, install the project dependencies.



    `pip install -r requirements.txt`


6.  Run the Application:

    Now, you can run the Flask app.



    `python3 app.py`

7.  Access the Application:

    Open a web browser and navigate to:


    `http://127.0.0.1:5000/`

    You should see the application running.

8.  Deactivate the Virtual Environment:

    Once done, you can deactivate the virtual environment to return to your global Python environment.



    `deactivate`

### Troubleshooting

-   If you encounter an error related to a missing package or dependency, ensure that the virtual environment is activated and you've installed all necessary packages using `pip install -r requirements.txt`.
-   If you experience issues related to environment variables (e.g., `SPOTIFY_CLIENT_ID` or `SPOTIFY_CLIENT_SECRET`), ensure they are properly set in your `.env` file and that you are using `python-dotenv` to load them. Just create an `.env` file in the root directory of the project and add the following lines, replacing the values with your own:

    `SPOTIFY_CLIENT_ID=your-client-id`

    `SPOTIFY_CLIENT_SECRET=your-client-secret`