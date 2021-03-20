Changes
- Inputs: From list of animes to list of genres; recommendation based on genres
- Added Search function for specific animes
- Changed avg_rating in anime to a function that calculates the average based on user ratings
  - First, we updated avg_rating with the calculated average.
  - Then, we created a trigger that updates avg_rating everytime a user rates an anime. 