### MATR FRONTEND

# ENV
docker login

# CONTAINER BUILD
docker build -t doc1024/matr:frontend-latest -f Dockerfile .
docker push doc1024/matr:frontend-latest

# CONTAINER RUN
docker pull doc1024/matr:frontend-latest
docker run --publish 3000:3000 --name matr-frontend -d doc1024/matr:frontend-latest

# CONTAINER STOP/KILL
docker stop matr-frontend
docker remove matr-frontend

# CONTAINER CONNECT
docker ps -all
docker exec -it matr-frontend /bin/bash

# APP INSTALL
npm install

# RUN FRONTEND
npm start



# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts
### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.


## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
