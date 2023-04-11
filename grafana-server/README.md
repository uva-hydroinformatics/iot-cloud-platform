# Grafana server
After deploying the Grafana server, you can access the Grafana web interface by creating a SSH tunnel to forward the server port 3000 to localhost:3000 and accesing the page http://localhost:3000 with a web browser. To obtain the server credentials, run the command "cat bitnami_credentials" in the home directory. 


# Initial setup

- Create a MySQL data source using the username and password created during the MySQL database configuration.
- Import a dashboard using the json file in the folder dashboard-example

# Example dashboard image

<img src="./images/water_level.jpg">