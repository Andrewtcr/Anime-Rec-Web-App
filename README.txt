Changes
- Inputs: From list of animes to list of genres; recommendation based on genres
- Added Search function for specific animes
- Changed avg_rating in anime to a function that calculates the average based on user ratings
  - First, we updated avg_rating with the calculated average (from the original dataset).
  - Then, we update avg_rating everytime a user rates an anime. 
- Users can edit and delete their own reviews and comments. (function; not stored in db)
- Admins can edit and delete all reviews and comments. (Only deleting reviews and modifying comments are stored)
  -> foreign key delete on cascade
- Recommendations only show 100 max 
