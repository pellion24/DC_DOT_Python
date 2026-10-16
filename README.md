## About the project

Python project from DC DOT 

## How to run 
Ensure you have python installed, and that you are in the root directory
```sh 
pip install pandas requests
```
Next
```sh
python3 main.py
```
There is also user-input required, read the message and press the enter key when prompted

---
## Narrative

- **First Steps:** It honestly took me a couple scans of the PDF to understand what was being asked of me, but once I got it I knew my next steps were to 
- **Postman:** Next I had to examine the APIs, their structures, and how ARCGIS web APIs differ from what I'm used to. After sending a few general requests to get a
different names that each of the 3 companies could have, I learned that I could filter out what I didn't need through the request itself using the WHERE parameter,
which saved me a couple lines of pandas code.
- **Pandas:** Getting the data back from the Occupancy Permit API was pretty simple, and only required some light cleaning, dropping the duplicate coordinate pairs. Next was
the Linear Referencing System, which stumped me for a bit. I knew I had around 700 coordinates that had to each be inputted as params for a request to the LRS, and
given that one request took around 5-7 seconds on postman, I knew it wouldn't be fast. I tried messing around with batches and multi-threading but to no avail.
- **CSV:** I went through a couple of iterations to examine the CSV output and see what need changing  
  - After my first iteration I realized I needed to include a line to filter out the alleys
  - when I tried the multi-threading approach my functional class column wouldn't
  populate, and I wasn't able to deduce the root cause

## Final Thoughts
Overall I found this Python Test to be challenging but also engaging, and it's made me excited to work on more transportation related projects!