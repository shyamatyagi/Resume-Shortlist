steps to run backend
1.first go to backend directory using 'cd' command
2.pip install -r requirements.txt
3.uvicorn main:app --reload

steps to run frontend
1.first go to frontend directory using 'cd' command
2.npm install
3.npm start

once the frontend start it will automatically pop window in your browser if does not then
http://localhost:3000/. --> paste this in browser

Flow of the project

1.  http://localhost:3000/admin
    admin will upload the csv file containing details of qualification
    pls refer test.csv

2.http://localhost:3000/
user will just upload canditates pdf ..and press shortlist button.
it will be shown in three color green , yello and red
